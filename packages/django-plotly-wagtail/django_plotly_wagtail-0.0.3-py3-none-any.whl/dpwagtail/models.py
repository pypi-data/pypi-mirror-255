"""
Django models for use with django-plotly-dash
"""
import json

from django.db import models
from django.contrib import admin
from django.utils.text import slugify

from wagtail.models import Page
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel

from django_plotly_dash.models import StatelessApp, DashApp


class InstanceBuilder(models.Model):
    """Builder of dash instances"""
    
    name = models.CharField(max_length=100, blank=False, unique=True, null=False)
    args = models.JSONField(blank=True, null=True)

    def __str__(self):
        return self.name

    def form_instance(self, name, specific_args, stateless_app):
        base_args = self.args if self.args else {}
        specific_args = specific_args if specific_args else {}
        actual_args = {**self.args,
                       **specific_args}

        non_app_args = actual_args.pop('__non_app', {})

        dapp = DashApp(stateless_app=stateless_app,
                       base_state=json.dumps(actual_args),
                       instance_name=name)

        if 'save_on_change' in non_app_args:
            dapp.save_on_change = non_app_args['save_on_change']

        dapp.save()

        return dapp
                       

class InstanceBuilderAdmin(admin.ModelAdmin):
    list_display = ['name', ]
    list_filter = []

    def _form_instance_builders(self, request, queryset):
        form_instance_builders(InstanceBuilder)

    _form_instance_builders.short_description = "Form instance builders"

    actions = ['_form_instance_builders',
               ]


class DashInstance(models.Model):
    """A description of a specific instance of a dash app"""

    IMC_STATELESS = 0
    IMC_PER_USER = 1
    INSTANCE_MODE_CHOICES = [(IMC_STATELESS, 'Stateless'),
                             (IMC_PER_USER, 'Per User'),
                             ]

    name = models.CharField(max_length=100, blank=False, unique=False, null=False)
    slug = models.SlugField(max_length=110, blank=True, unique=True, null=False)
    instance_builder = models.ForeignKey(InstanceBuilder,
                                         null=True,
                                         unique=False,
                                         on_delete=models.SET_NULL)
    stateless_app = models.ForeignKey(StatelessApp,
                                      null=True,
                                      unique=False,
                                      on_delete=models.SET_NULL)
    specific_args = models.JSONField(blank=True, null=True)
    instance_mode = models.PositiveSmallIntegerField(null=False,
                                                     default=IMC_STATELESS,
                                                     choices=INSTANCE_MODE_CHOICES,
                                                     blank=False,
                                                     unique=False)

    def instance_name(self, request):
        if self.instance_mode == DashInstance.IMC_STATELESS:
            return str(self.stateless_app)

        if self.instance_mode == DashInstance.IMC_PER_USER:
            user = request.user
            return f"{self.stateless_app} :user: {user.username}"

        # For now
        return str(self.stateless_app)

    def resolve_instance(self, request):
        """Determine the appropriate dash instance to use"""
        if self.instance_mode == DashInstance.IMC_STATELESS:
            return "name", self.stateless_app

        name = self.instance_name(request)
        existing = DashApp.objects.filter(instance_name=name)
        if existing.count() > 0:
            return "da", existing[0]

        # Need to form the instance
        dapp = self.instance_builder.form_instance(name,
                                                   self.specific_args,
                                                   self.stateless_app)
        return "da", dapp

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if len(self.slug) < 1:
            named_items = DashInstance.objects.filter(name=self.name).exclude(id=self.id)

            if named_items.count() > 0:
                ct = named_items.count()
                for r in range(ct, ct+20):
                    fname = f"{slugify(self.name)}-{r}"
                    if count(DashInstance.objects.filter(slug=fname)) < 1:
                        self.slug = fname
                        break
            else:
                self.slug = slugify(self.name)

        return super().save(*args, **kwargs)


class DashInstanceAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'stateless_app', 'instance_mode', 'instance_builder', ]
    list_filter = ['name', 'stateless_app', 'instance_mode', 'instance_builder', ]


class DjangoPlotlyDashIndexPage(Page):
    """Index page for a collection of DjangoPlotlyDashPage children"""

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context['dpd_pages'] = DjangoPlotlyDashPage.objects.child_of(self).live()
        return context


class DjangoPlotlyDashPage(Page):

    dash_instance = models.ForeignKey(DashInstance,
                                      null=True,
                                      unique=False,
                                      on_delete=models.SET_NULL)
    short_description = RichTextField(blank=True)
    description = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('dash_instance'),
        FieldPanel('short_description'),
        FieldPanel('description'),
    ]
