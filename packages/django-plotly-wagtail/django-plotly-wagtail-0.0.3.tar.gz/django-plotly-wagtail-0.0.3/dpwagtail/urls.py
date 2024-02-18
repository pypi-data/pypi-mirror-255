"""
Specific urls for django-plotly-wagtail pages
"""


from django.urls import path

import dpwagtail.dash_apps

from .app_name import app_name
from .views import InstanceBuilderListView


urlpatterns = [
    path('instance_builders/', InstanceBuilderListView.as_view(), name='instance-builders'),
]
