# coding=utf-8
"""
Missing batteries from Python
"""
from datetime import datetime
import inspect
import os
import random

from builtins import object
from past.builtins import basestring

from mock import Mock

from dateutil import parser

from pytz import utc


if hasattr(inspect, 'getfullargspec'): # pragma: nocover
    getargspec = inspect.getfullargspec
else: # pragma: nocover
    getargspec = inspect.getargspec


EMOJI = u'👻👾🤖😼💫👒🎩🐶🦎🐚🌸🌲🍋🥝🥑🥐🍿🥄⛺🚂🚲🌈🏆🎵💡✏🖍📌🛡♻'


def eachMethod(decorator, methodFilter=lambda fName: True):
    """
    Class decorator that wraps every single method in its own method decorator

    methodFilter: a function which accepts a function name and should return
    True if the method is one which we want to decorate, False if we want to
    leave this method alone.

    methodFilter can also be simply a string prefix. If it is a string, it is
    assumed to be the prefix we're looking for.
    """
    if isinstance(methodFilter, basestring):
        # Is it a string? If it is, change it into a function that takes a string.
        prefix = methodFilter
        methodFilter = lambda fName: fName.startswith(prefix)

    ismethod = lambda fn: inspect.ismethod(fn) or inspect.isfunction(fn)

    def innerDeco(cls):
        assert inspect.isclass(cls), "eachMethod is designed to be used only on classes"
        for fName, fn in inspect.getmembers(cls):
            if methodFilter(fName):
                if ismethod(fn):
                    # We attempt to avoid decorating staticmethods by looking for an arg named cls
                    # or self; this is a kludge, but there's no other way to tell, and
                    # staticmethods do not work correctly with eachMethod
                    if getargspec(fn).args[0] not in ['cls', 'self']:
                        continue

                    setattr(cls, fName, decorator(fn))

        return cls
    return innerDeco


class enum(dict):
    """
    Create a simple attribute list from keys
    """
    @classmethod
    def fromkeys(cls, keys):
        ret = cls()
        dd = []
        for k in keys:
            dd.append((k, k))
        ret.update(dict(dd))
        return ret

    def __getattr__(self, attr):
        try:
            return self[attr]
        except KeyError:
            raise AttributeError(attr)


def _sibpath(path, sibling):
    """
    Return the path to a sibling of a file in the filesystem.

    This is useful in conjunction with the special C{__file__} attribute
    that Python provides for modules, so modules can load associated
    resource files.

    (Stolen from twisted.python.util)
    """
    return os.path.join(os.path.dirname(os.path.abspath(path)), sibling)


class fromdir(object):
    """
    Swiss army knife for working with directory paths

    Returns a callable instance. Calls to the instance return paths from a
    preset directory.

    >>> fromcodado = fromdir('codado')
    >>> fromcodado('py.py')
    '/home/cory/src/Codado/codado/py.py'


    Also acts as a contextmanager that chdirs to the argument and returns
    self, the callable instance.

    >>> with fromdir('codado') as fromcodado:
    ...     print os.listdir('.')
    ...
    ['__init__.py', 'py.py', ..., 'py.pyc']


    When __init__ is called with multiple paths, they are joined.

    Also does ~homedir expansion, and accepts multiple path args to join.

    >>> print fromcodado('test', 'test_py.py')
    /home/cory/src/Codado/codado/test/test_py.py
    >>> print fromdir('~')('.bash_profile')
    /home/cory/.bash_profile


    As a final trick, if the argument is a file that exists, act like sibpath,
    and return paths relative to the dir that contains that file.

    (Only the argument is tested for existence and type.  In all other cases,
    this does only string manipulations and does not examine the filesystem.)

    >>> __file__ = '/home/cory/src/Codado/codado/__init__.py'
    >>> print fromdir(__file__)('tx.py')
    /home/cory/src/Codado/codado/tx.py
    >>> print fromdir(__file__, 'test')('test_tx.py')
    /home/cory/src/Codado/codado/test/test_tx.py


    Note the weird case that more than one argument is given, and more than
    one expands to a file; they are effectively discarded, and only the
    containing directory is used.

    >>> print fromdir(__file__, 'tx.py')('py.py')
    /home/cory/src/Codado/codado/py.py
    """
    def __init__(self, *paths):
        paths = list(paths)
        self.path = ''
        for cur in paths:
            cur = os.path.expanduser(cur)
            self.path = os.path.abspath(os.path.join(self.path, cur))

            if os.path.isfile(self.path):
                self.path = _sibpath(self.path, '')

    def __call__(self, *args):
        a = (self.path,) + args
        return os.path.join(*a)

    def __enter__(self):
        self._origDir = os.getcwd()
        os.chdir(self.path)
        return self

    def __exit__(self, type, value, tb):
        os.chdir(self._origDir)


def remoji():
    """
    Return a random, neutral emoji

    This list has been chosen to consist of emoji that have positive or neutral
    connotations, and which do not reflect any sort of identity symbols (e.g. no
    pictures of human beings). I have also tried to avoid symbols that have
    acquired punny or tasteless meanings, such as the eggplant emoji.

    I recognize that this list currently reflects my western bias. I am not confident
    that I can choose positive/neutral symbols from among the symbols that originate
    in non-western culture. Suggestions and updates to this list 100% welcome.
    """
    return random.choice(EMOJI)


def parseDate(dateString, strict=True):
    """
    Return a datetime object, by parsing a string date/time

    With strict=False, dateString may be None or '', otherwise it must be a
    parseable string
    """
    if (not strict) and (not dateString):
        return None

    if not isinstance(dateString, basestring):
        raise TypeError('%r is not a string' % dateString)

    return parser.parse(dateString)


def utcnowTZ():
    """
    Return a datetime (now), with UTC timezone, with tzinfo set
    """
    return datetime.utcnow().replace(tzinfo=utc)


class LottaPatches(object):
    """
    Patch a lot of things at once, managing cleanup afterwards
    Exposes all of the keyword arguments as mock objects for inspection,
    through the context variable.

    Use:

        patchContext = LottaPatches(
                mFoo=patch.object(foo, 'Foo'),
                mBar=patch.object(bar, 'Bar'))

        with patchContext as lots:
            ... run code ...

            lots.mFoo.assert_called_once_with(...)
            lots.mBar.assert_called_once_with(...)
    """
    def __init__(self, **patchers):
        self.patchers = patchers

    def __enter__(self):
        mocks = {}
        for name, p in list(self.patchers.items()):
            mocks[name] = p.start()

        return Mock(**mocks)

    def __exit__(self, type, value, tb):
        for p in list(self.patchers.values()):
            p.stop()
