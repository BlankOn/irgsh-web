from irgsh_web.basesettings import *
ROOT_URLCONF = 'irgsh_web.urls'

XMLRPC_METHODS = ()

import djcelery
djcelery.setup_loader()

