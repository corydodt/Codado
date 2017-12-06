"""
Common pytest workhorse code and fixtures
"""
from klein import Klein

from codado.kleinish import openAPIDoc, enter
from codado.kleinish.openapi import textHTML


class TopApp(object):
    app = Klein()

    @app.route('/sub/', branch=True)
    @enter('codado.test.conftest.SubApp')
    def subTree(self, request, subKlein):
        request.setHeader('content-type', 'application/topapp')
        return subKlein


class SubApp(object):
    app = Klein()

    @app.route('/idk', methods=['GET'])
    def idk(self, request): # pragma: nocover
        """
        This is an endpoint that can be filtered out

        It takes nothing and returns "idk"
        """
        return 'idk'

    @app.route('/end', methods=['POST', 'HEAD'])
    def end(self, request):
        """
        This is an endpoint

        It takes nothing and returns "ended"
        """
        return 'ended'

    @openAPIDoc(responses=textHTML({'x-page-class': 'codado.test.conftest.PageClass'}))
    @app.route('/end', methods=['GET'])
    def getEnd(self, request): # pragma: nocover
        """
        What is the end?

        This is the end.
        ---
        tags: [a, z]
        fish: [red, blue]
        """
        return 'status: unending'

    @openAPIDoc(responses={'default': {'content': {'text/html': {'x-page-class': 'codado.test.conftest.OtherPageClass'}}}})
    @app.route('/end', methods=['PUT'])
    def putEnd(self, request): # pragma: nocover
        # this has no docstring, for test coverage
        pass
