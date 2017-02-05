"""
Tests of the urltool command-line program
"""
import re

from pytest import fixture

from klein import Klein

from werkzeug.routing import Rule

from codado.kleinish import urltool, tree


def test_dumpRule():
    """
    Do I produce the correct data structure for a rule?
    """
    rule = Rule('/end/', endpoint='end')
    utr = urltool.dumpRule(Fnert, rule, '/fnert')
    expect = urltool.URLToolRule(
            endpoint='Fnert.end',
            rulePath='/fnert/end/',
            )
    assert utr == expect

    rule2 = Rule('/fnert/', endpoint='fnert_branch')
    utr2 = urltool.dumpRule(Blarb, rule2, '')
    expect2 = urltool.URLToolRule(
            endpoint='Blarb.fnert',
            rulePath='/fnert/',
            branch=True,
            subKlein='codado.test.test_urltool.Fnert',
            )
    assert utr2 == expect2


@fixture
def options():
    return urltool.Options()


class Blarb(object):
    app = Klein()

    @app.route('/fnert')
    @tree.enter('codado.test.test_urltool.Fnert')
    def fnert(self, request, subKlein):
        request.setHeader('content-type', 'application/blarb')
        return subKlein


class Fnert(object):
    app = Klein()

    @app.route('/end')
    def end(self, request):
        return 'hi'



def test_parseArgs(options):
    """
    Do I correct default the filter argument
    """
    options.parseArgs('codado.test.test_urltool.Blarb')
    assert options['filt'] == re.compile('.*')
    options.parseArgs('codado.test.test_urltool.Blarb', 'hello')
    assert options['filt'] == re.compile('hello')
