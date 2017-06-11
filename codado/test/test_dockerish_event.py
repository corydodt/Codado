"""
Tests of the dockerish event bus
"""
from pytest import fixture, mark

from mock import MagicMock

from codado.dockerish import event


@fixture
def dockerClientLowLevel():
    """
    A docker client mock
    """
    cli = MagicMock()
    cli.images = {'sha256:12345': 'animage'}
    cli.containers = {'12347': 'acontainer'}
    cli.networks = {'12349': 'anetwork'}
    cli.volumes = {'12351': 'avolume'}
    cli.plugins = {'12353': 'aplugin'}
    return cli


@fixture
def imageActorLowLevel():
    """
    The low-level dict of an image event actor from docker
    """
    return {"ID": "sha256:12345","Attributes": {"name": "sha256:12345"}}


@fixture
def imageEventLowLevel(imageActorLowLevel):
    """
    A low-level event from a docker image
    """
    return {
            "status": "delete",
            "id": "sha256:12345",
            "Type": "image",
            "Action": "delete",
            "Actor": imageActorLowLevel,
            "time": 1497218060,
            "timeNano": 1497218060835756369
            }


@fixture
def containerActorLowLevel():
    """
    The low-level dict of a container event actor from docker
    """
    return {
            "ID": "12347",
            "Attributes": {
                "image": "twist",
                "name": "peaceful_booth"
                }
            }


@fixture
def containerEventLowLevel(containerActorLowLevel):
    """
    A low-level event from a docker container
    """
    return {"status": "create",
            "id": "12347",
            "from": "abc123",
            "Type": "container",
            "Action": "create",
            "Actor": containerActorLowLevel,
            "time": 1497218188,
            "timeNano": 1497218188361178103
            }


@fixture
def networkActorLowLevel():
    return {
            "ID": "12349",
            "Attributes":
                {"container": "12347",
                 "name": "bridge",
                 "type": "bridge"
                 }
            }


@fixture
def networkEventLowLevel(networkActorLowLevel):
    return {
            "Type": "network",
            "Action": "connect",
            "Actor": networkActorLowLevel,
            "time": 1497218188,
            "timeNano": 1497218188440356384
            }


def test_fromLowLevelActor(imageActorLowLevel):
    """
    Do I construct an EventActor from a dict?
    """
    ea1 = event.EventActor.fromLowLevelActor(imageActorLowLevel)
    assert ea1 == event.EventActor(
            image=None,
            name='sha256:12345',
            signal=None,
            id='sha256:12345',
            )


def test_eventActorFromEventActor(imageActorLowLevel):
    """
    Do I pass through an EventActor unchanged?
    """
    ea1 = event.EventActor.fromLowLevelActor(imageActorLowLevel)
    ea2 = event.EventActor.fromLowLevelActor(ea1)
    assert ea2 == event.EventActor(
            image=None,
            name='sha256:12345',
            signal=None,
            id='sha256:12345',
            )


@mark.parametrize('llEvent,actorAttribute,expected', [
    ['containerEventLowLevel', 'container', 'acontainer'],
    ['networkEventLowLevel', 'network', 'anetwork'],
    ['imageEventLowLevel', 'image', 'animage'],
    ])
def test_eventProperties(dockerClientLowLevel, llEvent, actorAttribute,
        expected, request):
    """
    Do I get the right thing from the docker engine when I get a property
    from the event?
    """
    eng = MagicMock(client=dockerClientLowLevel)
    llEvent = request.getfixturevalue(llEvent)
    ev = event.Event.fromLowLevelEvent(eng, llEvent)
    assert getattr(ev, actorAttribute) == expected

