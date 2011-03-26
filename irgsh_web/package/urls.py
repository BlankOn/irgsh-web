from django.conf.urls.defaults import *

urlpatterns = patterns('irgsh_web.package.views',
    url(r'^(?P<package_name>[a-z0-9.-]+)/$',
        'show', name='package_show'),
    url(r'^$', 'index', name='package_index'),
)

