from django.conf.urls.defaults import *

TASK_ID = r'(?P<task_id>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})'

urlpatterns = patterns('irgsh_web.build.views',
    url(r'^(?P<spec_id>\d+)/$', 'spec_show', name='build_spec_show'),
    url(r'^(?P<spec_id>\d+)/description/$', 'spec_description', name='build_spec_description'),
    url(r'^(?P<spec_id>\d+)/status/$', 'spec_status', name='build_spec_status'),
    url(r'^%s/log/' % TASK_ID, 'task_log', name='build_task_log'),
    url(r'^%s/status/' % TASK_ID, 'task_status', name='build_task_status'),
    url(r'^%s/' % TASK_ID, 'task_show', name='build_task_show'),
    url(r'^submit/$', 'submit', name='build_submit'),
    url(r'^$', 'index', name='build_index'),
)

