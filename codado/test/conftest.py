"""
Common pytest workhorse code and fixtures
"""
from klein import Klein

from codado.kleinish import tree, openapi


class TopApp(object):
    app = Klein()

    @app.route('/sub/', branch=True)
    @tree.enter('codado.test.conftest.SubApp')
    def subTree(self, request, subKlein):
        request.setHeader('content-type', 'application/topapp')
        return subKlein


class SubApp(object):
    app = Klein()

    @app.route('/end', methods=['POST', 'HEAD'])
    def end(self, request):
        """
        This is an endpoint

        It takes nothing and returns "ended"
        """
        return 'ended'

    @app.route('/end', methods=['GET'])
    @tree.openapi(openapi.responses.default.textHTML({'x-page-class': 'codado.test.conftest.PageClass'}))
    def getEnd(self, request): # pragma: nocover
        """
        What is the end?

        This is the end.
        ---
        tags: [a, z]
        fish: [red, blue]
        """
        return 'status: unending'
