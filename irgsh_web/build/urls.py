from django.conf.urls.defaults import *

TASK_ID = r'(?P<task_id>\d+\.\d+\.\d+)'

urlpatterns = patterns('irgsh_web.build.views',
    url(r'^(?P<spec_id>\d+)/$', 'spec_show', name='build_spec_show'),
    url(r'^(?P<spec_id>\d+)/sources/(?P<path>.*)$', 'spec_source', name='build_spec_source'),
    url(r'^(?P<spec_id>\d+)/description/$', 'spec_description', name='build_spec_description'),
    url(r'^(?P<spec_id>\d+)/status/$', 'spec_status', name='build_spec_status'),
    url(r'^(?P<spec_id>\d+)/repo/status/$', 'repo_status', name='build_repo_status'),
    url(r'^task/%s/build.log.gz$' % TASK_ID, 'task_build_log', name='build_task_build_log'),
    url(r'^task/%s/(?P<path>.+_.+_.+\.changes)$' % TASK_ID, 'task_changes_file', name='build_task_changes_file'),
    url(r'^task/%s/log/$' % TASK_ID, 'task_log', name='build_task_log'),
    url(r'^task/%s/changes/$' % TASK_ID, 'task_changes', name='build_task_changes'),
    url(r'^task/%s/status/$' % TASK_ID, 'task_status', name='build_task_status'),
    url(r'^task/%s/$' % TASK_ID, 'task_show', name='build_task_show'),
    url(r'^submit/$', 'submit', name='build_submit'),
    url(r'^summary/$', 'summary', name='build_summary'),
    url(r'^user/(?P<name>[a-z0-9_-]+)/$', 'user_show', name='build_user_show'),
    url(r'^worker/\+ping/$', 'worker_ping', name='build_worker_ping'),
    url(r'^builder/(?P<name>[a-z0-9_-]+)/task/$', 'builder_task', name='build_builder_task'),
    url(r'^builder/(?P<name>[a-z0-9_-]+)/ping/$', 'builder_ping', name='build_builder_ping'),
    url(r'^builder/(?P<name>[a-z0-9_-]+)/$', 'builder_show', name='build_builder_show'),
    url(r'^builder/$', 'builder_list', name='build_builder_list'),
    url(r'^$', 'index', name='build_index'),
)

