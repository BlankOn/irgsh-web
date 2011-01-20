from setuptools import setup, find_packages

packages = ['irgsh_web']
packages += ['irgsh_web.%s' % pkg for pkg in find_packages('irgsh_web')]

setup(
    name = "irgsh-web",
    version = "0.2",
    url = 'http://irgsh.blankonlinux.or.id/',
    description = 'Ir. Robot Gedek, SH',
    author = 'BlankOn Developers',
    packages = packages,
    install_requires = ['setuptools', 'django-openid-auth', 'django-xmlrpc',
                        'python-openid', 'celery', 'django-celery',
                        'django-picklefield', 'poster',
                        'django-debug-toolbar']
)

