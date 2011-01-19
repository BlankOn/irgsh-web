from django.conf.urls.defaults import *

TASK_ID = r'(?P<task_id>[0-9a-zA-Z]{10})'

urlpatterns = patterns('irgsh_web.build.views',
    url(r'^(?P<spec_id>\d+)/$', 'spec_show', name='build_spec_show'),
    url(r'^(?P<spec_id>\d+)/description/$', 'spec_description', name='build_spec_description'),
    url(r'^(?P<spec_id>\d+)/status/$', 'spec_status', name='build_spec_status'),
    url(r'^(?P<spec_id>\d+)/repo/status/$', 'repo_status', name='build_repo_status'),
    url(r'^task/%s/log/' % TASK_ID, 'task_log', name='build_task_log'),
    url(r'^task/%s/status/' % TASK_ID, 'task_status', name='build_task_status'),
    url(r'^task/%s/' % TASK_ID, 'task_show', name='build_task_show'),
    url(r'^submit/$', 'submit', name='build_submit'),
    url(r'^$', 'index', name='build_index'),
)

