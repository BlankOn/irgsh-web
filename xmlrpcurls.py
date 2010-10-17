from django.conf.urls.defaults import *
from django.conf import settings


# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from jobs.views import *

urlpatterns = patterns('',
   (r'xmlrpc/$', 'django_xmlrpc.views.handle_xmlrpc',),
)

