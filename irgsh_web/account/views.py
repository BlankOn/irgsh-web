from django.contrib import auth
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.conf import settings
from django.template import RequestContext

def logout(request):
    auth.logout(request)
    context = {'full_logout_url': settings.FULL_LOGOUT_URL}
    return render_to_response('account/logout.html', context,
                              context_instance=RequestContext(request))

