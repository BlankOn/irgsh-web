from django.conf.urls.defaults import *

urlpatterns = patterns('irgsh_web.package.views',
    url(r'^$', 'index', name='package_index'),
)

