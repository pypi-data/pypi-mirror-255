from django.views.generic import ListView


from .models import InstanceBuilder


class InstanceBuilderListView(ListView):
    model = InstanceBuilder
