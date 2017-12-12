"""
Tests of the urltool command-line program
"""
import re
from inspect import cleandoc

import yaml

from pytest import fixture

from werkzeug.routing import Rule

from codado.kleinish import urltool
from codado.test.conftest import TopApp, SubApp


def test_dumpRule():
    """
    Do I produce the correct data structure for a rule?
    """
    rule = Rule('/end/', endpoint='end')
    cor = urltool.dumpRule(SubApp, rule, '/sub')
    expect = urltool.ConvertedRule(
            operationId='SubApp.end',
            rulePath='/sub/end/',
            doco=urltool.OpenAPIExtendedDocumentation('This is an endpoint\n\nIt takes nothing and returns "ended"')
            )
    assert cor == expect

    rule2 = Rule('/sub/', endpoint='subTree_branch')
    utr2 = urltool.dumpRule(TopApp, rule2, '')
    expect2 = urltool.ConvertedRule(
            operationId='TopApp.subTree',
            rulePath='/sub/',
            doco=urltool.OpenAPIExtendedDocumentation(''),
            branch=True,
            subKlein='codado.test.conftest.SubApp',
            )
    assert utr2 == expect2


@fixture
def options():
    return urltool.Options()


def test_parseArgs(options):
    """
    Do I correctly default the filter argument
    """
    options.parseArgs('codado.test.conftest.TopApp')
    assert options['filt'] == re.compile('.*')
    options.parseArgs('codado.test.conftest.TopApp', 'hello')
    assert options['filt'] == re.compile('hello')


def test_filter(options, capsys):
    """
    Do I filter correctly? Forwards and reverse?
    """
    options.parseArgs('codado.test.conftest.TopApp')
    options['filt'] = re.compile('hasqueryarg')
    options.postOptions()
    assert capsys.readouterr()[0].strip() == cleandoc("""
        openapi: 3.0.0
        info:
          title: TODO
          version: TODO
        paths:
          /sub/hasqueryarg:
            get:
              summary: This is an endpoint that can be filtered out
              description: |-
                This is an endpoint that can be filtered out

                It takes a query arg and returns it
              operationId: SubApp.hasQueryArg
              parameters:
              - in: query
                name: color
                required: true
    """)

    options['reverse'] = True
    options.postOptions()
    assert capsys.readouterr()[0].strip() == cleandoc("""
        openapi: 3.0.0
        info:
          title: TODO
          version: TODO
        paths:
          /sub/end:
            get:
              tags:
              - a
              - z
              summary: What is the end?
              description: |-
                What is the end?

                This is the end.
              operationId: SubApp.getEnd
              responses:
                default:
                  content:
                    text/html:
                      x-page-class: codado.test.conftest.PageClass
              x-fish:
              - red
              - blue
            post:
              summary: This is an endpoint
              description: |-
                This is an endpoint

                It takes nothing and returns "ended"
              operationId: SubApp.end
            put:
              operationId: SubApp.putEnd
              responses:
                default:
                  content:
                    text/html:
                      x-page-class: codado.test.conftest.OtherPageClass

        """)




def test_postOptions(options, capsys):
    """
    Do I produce some nicely-formatted output
    """
    options.parseArgs('codado.test.conftest.TopApp')
    options.postOptions()
    assert capsys.readouterr()[0].strip() == cleandoc("""
        openapi: 3.0.0
        info:
          title: TODO
          version: TODO
        paths:
          /sub/end:
            get:
              tags:
              - a
              - z
              summary: What is the end?
              description: |-
                What is the end?

                This is the end.
              operationId: SubApp.getEnd
              responses:
                default:
                  content:
                    text/html:
                      x-page-class: codado.test.conftest.PageClass
              x-fish:
              - red
              - blue
            post:
              summary: This is an endpoint
              description: |-
                This is an endpoint

                It takes nothing and returns "ended"
              operationId: SubApp.end
            put:
              operationId: SubApp.putEnd
              responses:
                default:
                  content:
                    text/html:
                      x-page-class: codado.test.conftest.OtherPageClass
          /sub/hasqueryarg:
            get:
              summary: This is an endpoint that can be filtered out
              description: |-
                This is an endpoint that can be filtered out

                It takes a query arg and returns it
              operationId: SubApp.hasQueryArg
              parameters:
              - in: query
                name: color
                required: true

        """)


def test_yamlMultilineString():
    """
    Do I properly represent strings using multiline syntax
    """
    obj = {'thing': 'a\nb'}
    assert yaml.dump(obj, default_flow_style=False) == 'thing: |-\n  a\n  b\n'
