"""
Tests of the openapi schema in kleinish
"""
from inspect import cleandoc

import yaml

from codado.kleinish import openapi


def test_orderedDict():
    """
    Do I keep the order of dicts?
    """
    dct = openapi.UnsortableOrderedDict()
    dct['a'] = 1
    dct['z'] = 2
    dct['b'] = 3
    dct['y'] = 4
    dct['c'] = 5
    dct['x'] = 6
    assert yaml.dump(dct, default_flow_style=False) == cleandoc('''
        a: 1
        z: 2
        b: 3
        y: 4
        c: 5
        x: 6
        ''') + '\n'
