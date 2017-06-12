"""
Run code from docker events


Usage:


from codado.dockerish import DockerEngine

class NomsMourner(object):
    engine = DockerEngine()

    @engine.handler("die")
    def onDie(self, event):
        if event.imageFrom.startswith('corydodt/noms'):
            print "Sadness, noms shut down"
            event.log()

engine.run()
"""

from codado.dockerish.event import DockerEngine
(DockerEngine,) # for pyflakes

