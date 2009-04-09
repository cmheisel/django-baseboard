from django.conf.urls.defaults import *

from django.views.generic.list_detail import object_list, object_detail

from baseboard.models import Dashboard

dashboard_list_args = {
    'queryset': Dashboard.objects.all(),
    'template_name': 'baseboard/dashboard_list.html',
    'allow_empty': True,
    'template_object_name': 'dashboard',
}

dashboard_detail_args = {
    'queryset': Dashboard.objects.all(),
    'template_name': 'baseboard/dashboard_detail.html',
    'template_object_name': 'dashboard',
}

urlpatterns = patterns('',
   url(r'^$', object_list, dashboard_list_args, name="dashboard_list"),
   url(r'^dashboard/(?P<slug>[-\w]+)/$', object_detail, dashboard_detail_args, name="dashboard_detail"),
)                      
