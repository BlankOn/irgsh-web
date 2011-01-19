from django.conf.urls.defaults import *
from django.core.urlresolvers import reverse
from django.conf import settings

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/', include(admin.site.urls)),
    (r'^o/', include('django_openid_auth.urls')),
    (r'^site-media/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT}),
    (r'^new-job', 'django.views.generic.simple.redirect_to',
        {'url': '/submit/'}),
)

TASK_ID = r'(?P<task_id>[0-9a-zA-Z]{10})'

urlpatterns += patterns('irgsh_web.build.views',
    # build spec
    url(r'^build/(?P<spec_id>\d+)/$', 'spec_show', name='build_spec_show'),
    url(r'^build/(?P<spec_id>\d+)/description/$', 'spec_description', name='build_spec_description'),
    url(r'^build/(?P<spec_id>\d+)/status/$', 'spec_status', name='build_spec_status'),
    url(r'^build/(?P<spec_id>\d+)/repo/status/$', 'repo_status', name='build_repo_status'),
    url(r'^build/$', 'spec_list', name='build_spec_list'),

    # build task
    url(r'^task/%s/log/' % TASK_ID, 'task_log', name='build_task_log'),
    url(r'^task/%s/status/' % TASK_ID, 'task_status', name='build_task_status'),
    url(r'^task/%s/' % TASK_ID, 'task_show', name='build_task_show'),

    # submit
    url(r'^submit/$', 'submit', name='build_submit'),

    # builder
    url(r'^builder/(?P<name>[a-z0-9_-]+)/$', 'builder_show', name='build_builder_show'),
    url(r'^builder/$', 'builder_list', name='build_builder_list'),

    # summary
    url(r'^$', 'summary', name='build_summary'),
)


# from irgsh_web.jobs.views import *
# 
# urlpatterns = patterns('',
#     # Example:
#     # (r'^web_builder/', include('web_builder.foo.urls')),
# 
#     # Uncomment the admin/doc line below and add 'djantgo.contrib.admindocs' 
#     # to INSTALLED_APPS to enable admin documentation:
#     # (r'^admin/doc/', include('django.contrib.admindocs.urls')),
# 
#     # Uncomment the next line to enable the admin:
#     (r'^admin/', include(admin.site.urls)),
#     (r'^build/', include('irgsh_web.build.urls')),
# 
#     (r'^o/', include('django_openid_auth.urls')),
#     (r'^logout/', site_logout),
#     ('^new-job/', new_job),
#     ('^builder/(?P<builder_id>.*)$', builder),
#     ('^task/(?P<task_id>.*)$', task),
#     ('^tasks/$', tasks),
#     (r'xmlrpc/$', 'django_xmlrpc.views.handle_xmlrpc',),
#     ('^$', site_index),
# )
# 
# urlpatterns += patterns('',
#     (r'^site-media/(?P<path>.*)$', 'django.views.static.serve',
#     {'document_root': settings.MEDIA_ROOT}),
# )

