"""
Tests of the urltool command-line program
"""
import re
from inspect import cleandoc

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
    expect = urltool.OpenAPIRule(
            endpoint='SubApp.end',
            rulePath='/sub/end/',
            summary='This is an endpoint',
            description='This is an endpoint\n\nIt takes nothing and returns hi'
            )
    assert utr == expect

    rule2 = Rule('/sub/', endpoint='subTree_branch')
    utr2 = urltool.dumpRule(TopApp, rule2, '')
    expect2 = urltool.OpenAPIRule(
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
    options.parseArgs('codado.test.conftest.TopApp')
    assert options['filt'] == re.compile('.*')
    options.parseArgs('codado.test.conftest.TopApp', 'hello')
    assert options['filt'] == re.compile('hello')


def test_postOptions(options, capsys):
    """
    Do I produce some nicely-formatted output
    """
    options.parseArgs('codado.test.conftest.TopApp')
    options.postOptions()
    assert capsys.readouterr()[0].strip() == cleandoc("""
        /sub/end:
          post:
            description: |-
              This is an endpoint

              It takes nothing and returns hi
            summary: This is an endpoint
        """)
