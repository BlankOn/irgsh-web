from setuptools import setup, find_packages

def get_version():
    import irgsh_web
    return irgsh_web.__version__

packages = ['irgsh_web']
packages += ['irgsh_web.%s' % pkg for pkg in find_packages('irgsh_web')]

setup(
    name = "irgsh-web",
    version = get_version(),
    url = 'http://irgsh.blankonlinux.or.id/',
    description = 'Ir. Robot Gedek, SH',
    author = 'BlankOn Developers',
    packages = packages,
    install_requires = ['setuptools', 'django-openid-auth', 'django-xmlrpc',
                        'python-openid', 'celery<2.2', 'django-celery<2.2',
                        'django-picklefield', 'poster', 'python-debian',
                        'django-debug-toolbar']
)

