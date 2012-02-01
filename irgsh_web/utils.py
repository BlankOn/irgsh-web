import urllib2
import urllib

from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, InvalidPage

from poster.encode import multipart_encode
from poster.streaminghttp import StreamingHTTPHandler, StreamingHTTPRedirectHandler, \
                                 StreamingHTTPSHandler, StreamingHTTPSConnection

class HTTPSHandler(StreamingHTTPSHandler):
    def __init__(self, debuglevel=0, key_file=None, cert_file=None):
        self.key_file = key_file
        self.cert_file = cert_file
        StreamingHTTPSHandler.__init__(self, debuglevel)

    def https_open(self, req):
        key_file = self.key_file
        cert_file = self.cert_file

        class HTTPSConnection(StreamingHTTPSConnection):
            def __init__(self, *args, **kwargs):
                if key_file is not None:
                    kwargs['key_file'] = key_file
                if cert_file is not None:
                    kwargs['cert_file'] = cert_file
                StreamingHTTPSConnection.__init__(self, *args, **kwargs)

        return self.do_open(HTTPSConnection, req)

def send_message(url, param=None):
    # Use poster's HTTP and HTTPS handler with additional support
    # for client certificate
    key_file = getattr(settings, 'SSL_KEY', None)
    cert_file = getattr(settings, 'SSL_CERT', None)
    handler = HTTPSHandler(key_file=key_file, cert_file=cert_file)

    handlers = [StreamingHTTPHandler, StreamingHTTPRedirectHandler, handler]
    opener = urllib2.build_opener(*handlers)

    # Construct data and headers
    data = None
    has_file = False
    headers = {}
    if param is not None:
        has_file = any([type(value) == file for value in param.values()])
        if has_file:
            data, headers = multipart_encode(param)
        else:
            data = urllib.urlencode(param)

    # Create request
    request = urllib2.Request(url, data, headers)
    return opener.open(request).read()

def paginate(queryset, total, page):
    try:
        page = int(page)
        if page < 0: page = 1
    except ValueError:
        page = 1

    paginator = Paginator(queryset, total)

    try:
        items = paginator.page(page)
    except (EmptyPage, InvalidPage):
        items = paginator.page(paginator.num_pages)

    return items

def tweet(message):
    try:
        import twitter
        conf = settings.TWITTER_CONFIG
        consumer_key = conf['CONSUMER_KEY']
        consumer_secret = conf['CONSUMER_SECRET']
        access_token_key = conf['ACCESS_TOKEN_KEY']
        access_token_secret = conf['ACCESS_TOKEN_SECRET']
    except (ImportError, TypeError, KeyError):
        return False

    if None in (consumer_key, consumer_secret,
                access_token_key, access_token_secret):
        return False

    try:
        api = twitter.Api(consumer_key=consumer_key,
                          consumer_secret=consumer_secret,
                          access_token_key=access_token_key,
                          access_token_secret=access_token_secret)
        api.PostUpdate(message)
        return True
    except (twitter.TwitterError, TypeError):
        return False

def build_short_url(path):
    return '%s/%s' % (settings.SHORT_URL.rstrip('/'), path.lstrip('/'))

def get_twitter_or_username(specification):
    user = specification.submitter
    profile = user.get_profile()

    if profile and profile.twitter:
        return '@%s' % profile.twitter
    return user.username

