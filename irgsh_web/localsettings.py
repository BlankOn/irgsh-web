# Sertifikat pekerja penyiap tugas
SSL_KEY = 'local/taskinit.key'
SSL_CERT = 'local/taskinit.pem'

# Konfigurasi antrian
BROKER_HOST = 'localhost'
BROKER_PORT = 5671
BROKER_USER = 'irgsh'
BROKER_PASSWORD = 'irgsh'
BROKER_VHOST = 'irgsh'

# Lokasi upload paket kode sumber
SOURCE_UPLOAD_HOST = 'rani.blankonlinux.or.id'
SOURCE_UPLOAD_USER = 'arsipdev'
SOURCE_UPLOAD_PORT = 2222
SOURCE_UPLOAD_KEY = 'local/taskinit-ssh.key'

# Lokasi Irgsh
SERVER = 'https://localhost:8000/'

# Lokasi penyimpanan log
LOG_PATH = 'run/logs'

# Lokasi paket kode sumber bagi pekerja
DOWNLOAD_TARGET = 'static/source/'

# Basis data
DATABASES = {
    'default': {
        'ENGINE': 'postgresql_psycopg2',
        'NAME': 'irgsh',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
	'HOST': 'localhost',
    },
    'dev': {
        'ENGINE': 'sqlite3',
        'NAME': 'irgsh.db',
    }
}

# SSO
## Set aku.boi host here
OPENID_CREATE_USERS = True
OPENID_UPDATE_DETAILS_FROM_SREG = True
LOGIN_URL = '/account/login'
LOGIN_REDIRECT_URL = '/'

# LOCAL DEVELOPMENT
OPENID_SSO_SERVER_URL = "http://localhost:3000/o/"
FULL_LOGOUT_URL = "http://localhost:3000/logout/"

# PRODUCTION
#OPENID_SSO_SERVER_URL = "https://aku.blankonlinux.or.id/o/"
#FULL_LOGOUT_URL = "https://aku.blankonlinux.or.id/logout/"

OPENID_USE_AS_ADMIN_LOGIN = True

TIME_ZONE = 'Asia/Jakarta'

# Twitter
TWITTER_CONFIG = dict(CONSUMER_KEY=None,
                      CONSUMER_SECRET=None,
                      ACCESS_TOKEN_KEY=None,
                      ACCESS_TOKEN_SECRET=None)

DEBUG = True

