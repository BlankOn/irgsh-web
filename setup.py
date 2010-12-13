from setuptools import setup, find_packages

setup(
    name = "irgsh-web",
    version = "0.2",
    url = 'http://irgsh.blankonlinux.or.id/',
    description = 'Ir. Robot Gedek, SH',
    author = 'BlankOn Developers',
    packages = ['irgsh_web'],
    install_requires = ['setuptools', 'django-openid-auth', 'django-xmlrpc']
)

