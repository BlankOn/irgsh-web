from django.conf.urls.defaults import *
from django.views.generic.simple import redirect_to
from django.conf import settings

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/', include(admin.site.urls)),
    (r'^o/', include('django_openid_auth.urls')),
    (r'^media/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT}),
    (r'^account/', include('irgsh_web.account.urls')),
    (r'package/', include('irgsh_web.package.urls')),
)

TASK_ID = r'(?P<task_id>\d+\.\d+\.\d+)'

urlpatterns += patterns('irgsh_web.build.views',
    # build spec
    url(r'^build/(?P<spec_id>\d+)/$', 'spec_show', name='build_spec_show'),
    url(r'^build/(?P<spec_id>\d+)/sources/(?P<path>.*)$', 'spec_source', name='build_spec_source'),
    url(r'^build/(?P<spec_id>\d+)/source\.log\.gz$', 'source_log', name='build_source_log'),
    url(r'^build/(?P<spec_id>\d+)/description/$', 'spec_description', name='build_spec_description'),
    url(r'^build/(?P<spec_id>\d+)/status/$', 'spec_status', name='build_spec_status'),
    url(r'^build/(?P<spec_id>\d+)/info/$', 'spec_info', name='build_spec_info'),
    url(r'^build/(?P<spec_id>\d+)/repo/status/$', 'repo_status', name='build_repo_status'),
    url(r'^build/(?P<spec_id>\d+)/repo/log/$', 'repo_log_submit', name='build_repo_log_submit'),
    url(r'^build/(?P<spec_id>\d+)/repo\.log\.gz$', 'repo_log', name='build_repo_log'),
    url(r'^build/$', 'spec_list', name='build_spec_list'),

    # build task
    url(r'^task/%s/build\.log\.gz$' % TASK_ID, 'task_build_log', name='build_task_build_log'),
    url(r'^task/%s/(?P<path>.+_.+_.+\.changes)$' % TASK_ID, 'task_changes_file', name='build_task_changes_file'),
    url(r'^task/%s/log/$' % TASK_ID, 'task_log', name='build_task_log'),
    url(r'^task/%s/changes/$' % TASK_ID, 'task_changes', name='build_task_changes'),
    url(r'^task/%s/status/$' % TASK_ID, 'task_status', name='build_task_status'),
    url(r'^task/%s/info/$' % TASK_ID, 'task_info', name='build_task_info'),
    url(r'^task/%s/claim/$' % TASK_ID, 'task_claim', name='build_task_claim'),
    url(r'^task/%s/$' % TASK_ID, 'task_show', name='build_task_show'),

    # submit
    url(r'^submit/$', 'submit', name='build_submit'),

    # worker
    url(r'^worker/\+ping/$', 'worker_ping', name='build_worker_ping'),

    # builder
    url(r'^builder/(?P<name>[a-z0-9_-]+)/task/$', 'builder_task', name='build_builder_task'),
    url(r'^builder/(?P<name>[a-z0-9_-]+)/ping/$', 'builder_ping', name='build_builder_ping'),
    url(r'^builder/(?P<name>[a-z0-9_-]+)/$', 'builder_show', name='build_builder_show'),
    url(r'^builder/$', 'builder_list', name='build_builder_list'),

    # authorized keys
    url(r'^data/authorized_keys.json$', 'authorized_keys', name='build_authorized_keys'),

    # users
    url(r'^user/(?P<name>[a-z0-9_-]+)/$', 'user_show', name='build_user_show'),

    # shortcuts
    (r'^(?P<spec_id>\d+)/$', redirect_to, {'url': '/build/%(spec_id)s/',
                                           'permanent': True}),
    (r'^%s/$' % TASK_ID, redirect_to, {'url': '/task/%(task_id)s/',
                                       'permanent': True}),

    # summary
    url(r'^$', 'summary', name='build_summary'),
)

