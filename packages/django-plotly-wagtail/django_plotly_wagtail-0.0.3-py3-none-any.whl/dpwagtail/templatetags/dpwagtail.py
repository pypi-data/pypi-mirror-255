"""
Tags for rendering dash apps
"""


from django import template


register = template.Library()


@register.inclusion_tag("dpwagtail/tags/dpw_instance.html", takes_context=True)
def dpd_instance(context, dash_instance):
    request = context.get('request')
    app_args = dash_instance.resolve_instance(request)
    name, ivalue = app_args

    if name == 'da':
        is_dash_app = True
    if name == 'name':
        is_stateless_app = True

    return locals()


@register.inclusion_tag("dpwagtail/tags/dpd_page_short_listing.html", takes_context=True)
def dpd_page_short_listing(context, dpd_page):

    return locals()
