"""
Tests of the tree decorators in kleinish
"""
from pytest import inlineCallbacks

from mock import Mock

from codado.test.conftest import TopApp


@inlineCallbacks
def test_enter():
    """
    Do I return a subKlein resource when I access the subTree endpoint?
    Do I also run the code in the endpoint?
    """
    top = TopApp()
    mRequest = Mock()
    res = yield top.app.execute_endpoint('subTree', mRequest)
    assert 'end' in res._app.endpoints
    mRequest.setHeader.assert_called_once_with(
            'content-type',
            'application/topapp')

    res = yield res._app.execute_endpoint('end', Mock())
    assert res == 'ended'
