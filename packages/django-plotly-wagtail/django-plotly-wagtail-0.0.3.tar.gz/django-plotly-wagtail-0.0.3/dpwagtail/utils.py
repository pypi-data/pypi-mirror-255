"""
Utility functions
"""


def form_instance_builders(InstanceBuilder):
    """Create and add instance builders.

    The model is passed in, and not imported, so this function can
    be executed from a view.
    """

    items = {'Trivial no-arguments': {'args': {}},
             }

    res = []
    for name, kwargs in items.items():
        if InstanceBuilder.objects.filter(name=name).count() > 0:
            res.append((name, 0))
        else:
            ib = InstanceBuilder(name=name,
                                 **kwargs)
            ib.save()
            res.append((name, 1))
    return res


def _DUMP_DICT(d):
    for k, v in d.items():
        print(f"{k} : {v}")


def form_app_pages(ContentType, DjangoPlotlyDashIndexPage, DjangoPlotlyDashPage, Site, *args, **kwargs):
    """Form application pages within the Wagail CMS structure"""

    root = DjangoPlotlyDashIndexPage.get_first_root_node()
    content_type = ContentType.objects.get_for_model(DjangoPlotlyDashIndexPage)

    dpd_root_slug = "dpd-wagtail-index"
    hostname = "localhost"

    do_create = True

    for child in root.get_children():
        if child.slug == dpd_root_slug:
            do_create = False
            dpd_root_page = child

    if do_create:
        dpd_root_page = DjangoPlotlyDashIndexPage(content_type=content_type,
                                                  title="DPD Index",
                                                  draft_title="DPD Index",
                                                  slug=dpd_root_slug,
                                                  show_in_menus=True,
                                                  )
        root.add_child(instance=dpd_root_page)

    all_sites = Site.objects.all()
    dpd_sites = all_sites.filter(hostname=hostname)
    existing = True if dpd_sites.count() > 0 else False
    any_existing = True if all_sites.count() > 0 else False

    if existing:
        for s in dpd_sites:
            s.root_page = dpd_root_page
            s.site_name = "Django Plotly Dash Wagtail"
            s.save()
    else:
        site = Site.objects.create(hostname=hostname,
                                   root_page=dpd_root_page,
                                   is_default_site=True if not any_existing else False,
                                   site_name="Django Plotly Dash Wagtail")
        site.save()
