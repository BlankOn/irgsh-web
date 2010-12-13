from setuptools import setup, find_packages

console_scripts = [
    'irgsh-www = irgsh_web.bin.www:main',
    'irgsh-xmlrpc = irgsh_web.bin.xmlrpc:main',
]
packages = ['irgsh_web']
packages += ['irgsh_web.%s' % pkg for pkg in find_packages('irgsh_web')]

setup(
    name = "irgsh-web",
    version = "0.2",
    url = 'http://irgsh.blankonlinux.or.id/',
    description = 'Ir. Robot Gedek, SH',
    author = 'BlankOn Developers',
    packages = packages,
    entry_points = {'console_scripts': console_scripts},
    install_requires = ['setuptools', 'django-openid-auth', 'django-xmlrpc',
                        'python-openid']
)

