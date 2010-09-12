from django.conf.urls.defaults import *
from django.conf import settings


# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from jobs.views import *

urlpatterns = patterns('',
    # Example:
    # (r'^web_builder/', include('web_builder.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
    (r'^o/', include('django_openid_auth.urls')),
    (r'^logout/', site_logout),
    ('^new-job/', new_job),
    ('^task/(?P<task_id>.*)$', task),
    ('^$', site_index),
)

urlpatterns += patterns('',
    (r'^site-media/(?P<path>.*)$', 'django.views.static.serve',
    {'document_root': settings.MEDIA_ROOT}),
)
