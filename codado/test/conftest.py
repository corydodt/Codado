"""
Common pytest workhorse code and fixtures
"""

from klein import Klein

from codado.kleinish import tree


class TopApp(object):
    app = Klein()

    @app.route('/sub/', branch=True)
    @tree.enter('codado.test.conftest.SubApp')
    def subTree(self, request, subKlein):
        request.setHeader('content-type', 'application/topapp')
        return subKlein


class SubApp(object):
    app = Klein()

    @app.route('/end')
    def end(self, request):
        return 'hi'
