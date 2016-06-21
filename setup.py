from setuptools import setup

from codado import _version

setup(
  name = 'Codado',
  packages = ['codado'],
  version = _version.__version__,
  description = 'A collection of system development utilities',
  author = 'Cory Dodt',
  author_email = 'corydodt@gmail.com',
  url = 'https://github.com/corydodt/Codado',
  keywords = ['twisted', 'utility'],
  classifiers = [],
)
