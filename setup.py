from distutils.core import setup

from codado import _version

setup(
  name = 'Codado',
  packages = ['codado'],
  use_incremental = True,
  version = _version.__version__.base(),
  setup_requires = ['incremental'],
  install_requires = ['incremental'],
  description = 'A collection of system development utilities',
  author = 'Cory Dodt',
  author_email = 'corydodt@gmail.com',
  url = 'https://github.com/corydodt/Codado',
  keywords = ['twisted', 'utility'],
  classifiers = [],
)
