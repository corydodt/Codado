from setuptools import setup

from pip.req import parse_requirements

from codado import _version


reqs = parse_requirements('requirements.txt')

setup(
  name = 'Codado',
  packages = ['codado', 'codado.kleinish'],
  version = _version.__version__,
  description = 'A collection of system development utilities',
  author = 'Cory Dodt',
  author_email = 'corydodt@gmail.com',
  url = 'https://github.com/corydodt/Codado',
  keywords = ['twisted', 'utility'],
  classifiers = [],
  scripts = ['bin/urltool', 'bin/jentemplate'],
  install_requires=list(reqs)
)
