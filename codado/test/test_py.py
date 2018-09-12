# coding=utf-8
"""
Tests of codado.py
"""
from __future__ import print_function

from datetime import datetime
import os

from builtins import range, object

import wrapt

from mock import patch

from pytest import raises

from codado import py


def test_fromdir():
    """
    Does fromdir fulfill all of its responsibilities?

    - callable to find files
    - chdir contextmanager
    - join arguments and expand paths
    - sibpath-like behavior
    """
    cwd = os.path.dirname(__file__)
    fromtest = py.fromdir(__file__)

    parent = os.path.dirname(cwd)
    fromparent = py.fromdir(parent)
    print(fromparent(''))

    # callable joins files, and,
    # a fromdir() instance with a file argument acts like sibpath
    assert fromtest('test_py.py') == os.sep.join([cwd, 'test_py.py'])

    # contextmanager changes directories and returns a fromdir()
    assert 'py.py' not in os.listdir('.')
    with py.fromdir(parent) as fromparent:
        assert fromparent('__init__.py') == os.sep.join([parent, '__init__.py'])
        assert 'py.py' in os.listdir('.')

    # a fromdir() instance joins paths
    assert fromparent('test', 'test_py.py') == os.sep.join([parent, 'test', 'test_py.py'])

    # a fromdir() instance expands ~
    assert py.fromdir('~')() == os.environ['HOME']


def test_enum():
    """
    Do I permit attribute access to keys?
    Do I implement fromkeys as k=k?
    Do I raise Exceptions consistent with Python expectations?
    """
    en = py.enum.fromkeys(['a', 'b', '230489'])
    assert en.a == 'a'
    assert getattr(en, '230489') == '230489'
    assert en['b'] == 'b'

    en2 = py.enum({'a': 1, 'b': 2})
    assert en2.b == 2

    with raises(AttributeError):
        getattr(en2, 'asdf')
    with raises(KeyError):
        en2.__getitem__('asdf')


def test_eachMethod():
    """
    Does eachMethod properly handle unbound methods?
    Does eachMethod not wrap classmethod and staticmethod?
    Does eachMethod properly handle arguments the function is called with?
    """
    @wrapt.decorator
    def deco(wrapped, instance, args, kwargs):
        return ['deco', wrapped(*args, **kwargs)]

    @py.eachMethod(deco, 't_')
    class T(object):
        @staticmethod
        def t_s(val):
            """
            I should not be wrapped because I am a staticmethod
            """
            return 't_s' + val

        @classmethod
        def t_cm(cls, val):
            return 't_cm' + cls.__name__ + val

        def t_a(self):
            """
            I should be wrapped
            """
            return 'a'

        def t_b(self, val):
            """
            I should be wrapped and pass through a value
            """
            return 'b' + val

        def c(self):
            """
            I should not be wrapped because I do not contain the prefix
            """
            return 'c'

    tt = T()

    assert tt.t_a() == ['deco', 'a']
    assert tt.t_b('123') == ['deco', 'b123']
    assert tt.c() == 'c'
    assert tt.t_s('abc') == 't_sabc'
    assert T.t_s('abc') == 't_sabc'

    assert tt.t_cm('abc') == ['deco', 't_cmTabc']
    assert T.t_cm('abc') == ['deco', 't_cmTabc']


def test_remoji():
    """
    Does it get a stringy, emoji-y string randomly?
    """
    for n in range(100):
        choice = py.remoji() + py.remoji()
        assert isinstance(choice, type(u''))
        assert len(choice) == 2
        assert choice[1] in py.EMOJI


def test_parseDate():
    """
    Can I convert a basestring to a datetime object?
    """
    dateString = '2016-05-02T14:41:14.029622'
    expected = datetime(2016, 5, 2, 14, 41, 14, 29622)
    result = py.parseDate(dateString)
    assert result == expected

    # info includes timezone? result should have tzinfo attached
    dateString = '2016-05-02T14:41:14.029622Z'
    result = py.parseDate(dateString)
    assert result.tzinfo

    # None is returned ONLY if strict=False
    dateString = None
    raises(TypeError, py.parseDate, dateString)

    dateString = None
    expected = None
    result = py.parseDate(dateString, strict=False)
    assert result == expected


def test_utcnowTZ():
    """
    Do I add return a time with a timezone?
    """
    now = py.utcnowTZ()
    assert now.tzinfo


def test_lottaPatches():
    """
    Do I patch multiple things at once?
    """
    patchContext = py.LottaPatches(
            mParseDate=patch.object(py, 'parseDate'),
            mUTCNow=patch.object(py, 'utcnowTZ'))

    with patchContext as lots:
        py.parseDate('a', 'b')
        py.utcnowTZ()

        lots.mParseDate.assert_called_once_with('a', 'b')
        lots.mUTCNow.assert_called_once_with()
