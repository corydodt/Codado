"""
Tests of the urltool command-line program
"""
import re

from pytest import fixture

from werkzeug.routing import Rule

from codado.kleinish import urltool
from codado.test.conftest import TopApp, SubApp


def test_dumpRule():
    """
    Do I produce the correct data structure for a rule?
    """
    rule = Rule('/end/', endpoint='end')
    utr = urltool.dumpRule(SubApp, rule, '/sub')
    expect = urltool.URLToolRule(
            endpoint='SubApp.end',
            rulePath='/sub/end/',
            )
    assert utr == expect

    rule2 = Rule('/sub/', endpoint='subTree_branch')
    utr2 = urltool.dumpRule(TopApp, rule2, '')
    expect2 = urltool.URLToolRule(
            endpoint='TopApp.subTree',
            rulePath='/sub/',
            branch=True,
            subKlein='codado.test.conftest.SubApp',
            )
    assert utr2 == expect2


@fixture
def options():
    return urltool.Options()


def test_parseArgs(options):
    """
    Do I correct default the filter argument
    """
    options.parseArgs('codado.test.test_urltool.Blarb')
    assert options['filt'] == re.compile('.*')
    options.parseArgs('codado.test.test_urltool.Blarb', 'hello')
    assert options['filt'] == re.compile('hello')
