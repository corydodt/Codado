from inspect import cleandoc

from setuptools import setup

_version = {}
execfile('codado/_version.py', _version)

setup(
    name = 'Codado',
    packages = ['codado', 'codado.kleinish'],
    version = _version['__version__'],
    description = 'A collection of system development utilities',
    author = 'Cory Dodt',
    author_email = 'corydodt@gmail.com',
    url = 'https://github.com/corydodt/Codado',
    keywords = ['twisted', 'utility'],
    classifiers = [],
    scripts = ['bin/jentemplate'],
    install_requires=cleandoc('''
        attrs>=17.1.0
        crosscap
        jinja2
        mock>=2.0.0,<2.1.0
        python-dateutil==2.4.0
        pytz==2015.4
        pyyaml
        ''').split()
)
