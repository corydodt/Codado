"""
Tests of the dockerish event bus
"""
import time

from builtins import object

from pytest import fixture, mark

from mock import MagicMock, patch

from twisted.internet import task

import docker

from codado.dockerish import event


@fixture
def dockerClientLowLevel():
    """
    A docker client mock
    """
    cli = MagicMock()
    class Items(object):
        def __init__(self, dct):
            self.dct = dct

        def get(self, key):
            ret = self.dct.get(key)
            if ret is None:
                raise docker.errors.NotFound(key)
            return ret
 
    cli.images = Items({'sha256:12345': 'animage'})
    cli.containers = Items({'12347': 'acontainer'})
    cli.networks = Items({'12349': 'anetwork'})
    cli.volumes = Items({'12351': 'avolume'})
    cli.plugins = Items({"vieux/sshfs": 'aplugin'})
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
def containerActorDestroyLowLevel():
    """
    The low-level dict of a container event actor from docker
    """
    return {
            "ID": "deadbeef",
            "Attributes": {
                "image": "twist",
                "name": "peaceful_booth"
                }
            }


@fixture
def containerEventDestroyLowLevel(containerActorDestroyLowLevel):
    """
    A low-level event from a docker container
    """
    return {"status": "create",
            "id": "deadbeef",
            "from": "abc123",
            "Type": "container",
            "Action": "destroy",
            "Actor": containerActorDestroyLowLevel,
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


@fixture
def networkActorDestroyLowLevel():
    return {
            "ID": "deadcafe",
            "Attributes":
                {"container": "12347",
                 "name": "bridge",
                 "type": "bridge"
                 }
            }


@fixture
def networkEventDestroyLowLevel(networkActorDestroyLowLevel):
    return {
            "Type": "network",
            "Action": "destroy",
            "Actor": networkActorDestroyLowLevel,
            "time": 1497218188,
            "timeNano": 1497218188440356384
            }


@fixture
def daemonActorLowLevel():
    """
    This is a total guess, there doesn't seem to be any information about the
    'daemon.reload' event in the wild, and kill -HUP doesn't trigger it, so I
    don't know how to actually see one.
    """
    return {
            "ID": "0",
            "Attributes": {},
            }


@fixture
def daemonEventLowLevel(daemonActorLowLevel):
    return {
            "Type": "daemon",
            "Action": "reload",
            "Actor": daemonActorLowLevel,
            "time": 1497218188,
            "timeNano": 1497218188440356384
            }


@fixture
def volumeActorLowLevel():
    """
    This is a total guess, there doesn't seem to be any information about the
    'daemon.reload' event in the wild, and kill -HUP doesn't trigger it, so I
    don't know how to actually see one.
    """
    return {"ID": "12351",
            "Attributes": {"driver": "local"}
            }


@fixture
def volumeEventLowLevel(volumeActorLowLevel):
    return {"Type": "volume",
            "Action": "create",
            "Actor": volumeActorLowLevel,
            "time": 1497225755,
            "timeNano": 1497225755984676913
            }


@fixture
def pluginActorLowLevel():
    return {"ID": "vieux/sshfs:latest",
            "Attributes":{"name": "vieux/sshfs"}
            }


@fixture
def pluginEventLowLevel(pluginActorLowLevel):
    return {"Type": "plugin",
            "Action": "pull",
            "Actor": pluginActorLowLevel,
            "time": 1497225462,
            "timeNano": 1497225462002014924
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


@mark.parametrize('llEvent,actorAttribute,expected,name', [
    ['containerEventLowLevel', 'container', 'acontainer', 'container.create'],
    ['networkEventLowLevel', 'network', 'anetwork', 'network.connect'],
    ['imageEventLowLevel', 'image', 'animage', 'image.delete'],
    ['pluginEventLowLevel', 'plugin', 'aplugin', 'plugin.pull'],
    ['volumeEventLowLevel', 'volume', 'avolume', 'volume.create'],
    ['containerEventDestroyLowLevel', 'container', None, 'container.destroy'],
    ['networkEventDestroyLowLevel', 'network', None, 'network.destroy'],
    ])
def test_eventProperties(dockerClientLowLevel, llEvent, actorAttribute,
        expected, name, request):
    """
    Do I get the right thing from the docker engine when I get a property
    from the event?
    """
    eng = MagicMock(client=dockerClientLowLevel)
    llEvent = request.getfixturevalue(llEvent)
    ev = event.Event.fromLowLevelEvent(eng, llEvent)
    assert getattr(ev, actorAttribute) == expected
    assert ev.name == name


def test_daemonEvent(dockerClientLowLevel, daemonEventLowLevel):
    """
    Does the daemon.reload event work?

    n.b. I haven't been able to test this code in the wild.
    """
    eng = MagicMock(client=dockerClientLowLevel)
    ev = event.Event.fromLowLevelEvent(eng, daemonEventLowLevel)
    assert ev.daemon is eng.client
    assert ev.name == 'daemon.reload'


def test_dockerEngineDescriptor():
    """
    Do I bind to a class I'm an attribute of?
    """
    eng = event.DockerEngine()
    class EventConsumerApp(object):
        engine = eng

    # prior to instantion, owner is left unset
    assert EventConsumerApp.engine is eng
    assert not hasattr(eng, 'owner')

    app = EventConsumerApp()
    assert app.engine is eng
    # now owner is set
    assert eng.owner is app


def test_dockerEngineBindEvent(
        containerEventDestroyLowLevel,
        networkEventDestroyLowLevel):
    """
    Do I run methods when an event appears?
    """
    eng = event.DockerEngine()
    clock = task.Clock()
    eng.callLater = clock.callLater
    calls = []
    class EventConsumerApp(object):
        engine = eng

        @engine.handler("container.destroy")
        @engine.handler("network.destroy")
        def onDestroy(self, event):
            calls.append(('onDestroy', event.name, event.id))

        @engine.handler("dockerish.init")
        def onInit(self, event):
            calls.append(('onInit', event.name, event.id))

        @engine.defaultHandler
        def onAnyEvent(self, event):
            calls.append(('onAnyEvent', event.name, event.id))

    app = EventConsumerApp()

    now = time.time()

    app.engine.run()
    pClientEvents = patch.object(eng.client, 'events', autospec=True, 
        side_effect = [
            [containerEventDestroyLowLevel], # advance 1
            [networkEventDestroyLowLevel], # advance 2
            ]
        )
    with pClientEvents:
        clock.advance(now + 1)
        assert calls == [
                ('onAnyEvent', 'dockerish.init', None),
                ('onInit', 'dockerish.init', None),
                ('onAnyEvent', 'container.destroy', 'deadbeef'),
                ('onDestroy', 'container.destroy', 'deadbeef'),
                ]
        clock.advance(now + 2)
        assert calls[4:] == [
                ('onAnyEvent', 'network.destroy', None),
                ('onDestroy', 'network.destroy', None),
                ]
