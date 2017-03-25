import random

from twisted.internet import protocol
from twisted.internet import reactor
from twisted.protocols.basic import LineReceiver

from hockey.action import Action

from client import HockeyClient, ClientFactory

class RochesterClient(HockeyClient):
    def move(self):
        return Action.from_number(random.randint(0, 7))

class RochesterClientFactory(ClientFactory):
    def __init__(self, debug):
        self.name =  "Canadian Immigrants"
        self.debug = debug

    def buildProtocol(self, addr):
        return RochesterClient(self.name, self.debug)



