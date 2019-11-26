from inspect import cleandoc

from setuptools import setup


__version__ = '0.7.4'


cfg = dict(
    name = 'Codado',
    packages = ['codado'],
    version = __version__,
    description = 'A collection of system development utilities',
    author = 'Cory Dodt',
    author_email = 'corydodt@gmail.com',
    url = 'https://github.com/corydodt/Codado',
    keywords = ['twisted', 'utility'],
    classifiers = [
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License"
    ],
    scripts = ['bin/jentemplate'],
    install_requires=cleandoc('''
        attrs>=17.1.0
        crosscap
        jinja2
        mock>=2.0.0,<2.1.0
        python-dateutil
        pytz>=2015.4
        pyyaml
        twisted
        ''').split(),
    extras_require={
        'dev': [
            'tox',
            'pytest',
            'pytest-coverage',
            'pytest-flakes',
            'pytest-twisted',
            'klein',
            'docker',
            'wrapt',
        ]
    },
    zip_safe=False,
)


setup(**cfg)
