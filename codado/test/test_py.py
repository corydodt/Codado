"""
Tests of codado.py
"""
import os
from unittest import TestCase
from functools import wraps

from codado import py


class TestPy(TestCase):
    """
    Tests of codado.py
    """
    def test_fromdir(self):
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
        print fromparent('')

        # callable joins files, and,
        # a fromdir() instance with a file argument acts like sibpath
        self.assertEqual(fromtest('test_py.py'),
                os.sep.join([cwd, 'test_py.py']))

        # contextmanager changes directories and returns a fromdir()
        self.assertFalse('py.py' in os.listdir('.'))
        with py.fromdir(parent) as fromparent:
            self.assertEqual(fromparent('__init__.py'),
                    os.sep.join([parent, '__init__.py']))
            self.assertTrue('py.py' in os.listdir('.'))

        # a fromdir() instance joins paths
        self.assertEqual(fromparent('test', 'test_py.py'),
                os.sep.join([parent, 'test', 'test_py.py']))

        # a fromdir() instance expands ~
        self.assertEqual(py.fromdir('~')(), os.environ['HOME'])

    def test_enum(self):
        """
        Do I permit attribute access to keys?
        Do I implement fromkeys as k=k?
        Do I raise Exceptions consistent with Python expectations?
        """
        en = py.enum.fromkeys(['a', 'b', '230489'])
        self.assertEqual(en.a, 'a')
        self.assertEqual(getattr(en, '230489'), '230489')
        self.assertEqual(en['b'], 'b')

        en2 = py.enum({'a': 1, 'b': 2})
        self.assertEqual(en2.b, 2)

        self.assertRaises(AttributeError, getattr, en2, 'asdf')
        self.assertRaises(KeyError, en2.__getitem__, 'asdf')

    def test_eachMethod(self):
        """
        Does eachMethod properly handle unbound methods?
        Does eachMethod not wrap classmethod and staticmethod?
        Does eachMethod properly handle arguments the function is called with?
        """
        def deco(fn):
            fClass = fn.im_class

            if fClass is type:
                @wraps(fn)
                def boundClassmethod(bound, *a, **kw):
                    return ['deco', fn(*a, **kw)]

                inner = boundClassmethod

            else:
                @wraps(fn)
                def unboundInstancemethod(bound, *a, **kw):
                    return ['deco', fn(bound, *a, **kw)]

                inner = unboundInstancemethod

            return inner

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

        self.assertEqual(tt.t_a(), ['deco', 'a'])
        self.assertEqual(tt.t_b('123'), ['deco', 'b123'])
        self.assertEqual(tt.c(), 'c')
        self.assertEqual(tt.t_s('abc'), 't_sabc')
        self.assertEqual(T.t_s('abc'), 't_sabc')

        self.assertEqual(tt.t_cm('abc'), ['deco', 't_cmTabc'])
        self.assertEqual(T.t_cm('abc'), ['deco', 't_cmTabc'])
