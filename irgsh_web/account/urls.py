from django.conf.urls.defaults import *

urlpatterns = patterns('django_openid_auth.views',
    url(r'^login/$', 'login_begin', name='account_login'),
)
urlpatterns += patterns('irgsh_web.account.views',
    url(r'^logout/$', 'logout', name='account_logout'),
)

