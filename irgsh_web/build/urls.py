from django.conf.urls.defaults import *

TASK_ID = r'(?P<task_id>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})'

urlpatterns = patterns('irgsh_web.build.views',
    url(r'^(?P<spec_id>\d+)/$', 'show_spec', name='build_show_spec'),
    url(r'^(?P<spec_id>\d+)/description/$', 'spec_description', name='build_spec_description'),
    url(r'^(?P<spec_id>\d+)/status/$', 'spec_status', name='build_spec_status'),
    url(r'^%s/description/' % TASK_ID, 'description', name='build_description'),
    url(r'^%s/log/' % TASK_ID, 'build_log', name='build_log'),
    url(r'^%s/status/' % TASK_ID, 'update_status', name='build_update_status'),
    url(r'^%s/' % TASK_ID, 'show', name='build_show'),
    url(r'^submit/$', 'submit', name='build_submit'),
    url(r'^$', 'index', name='build_index'),
)

