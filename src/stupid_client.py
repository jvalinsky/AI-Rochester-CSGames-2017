import random

from twisted.internet import protocol
from twisted.internet import reactor
from twisted.protocols.basic import LineReceiver

from hockey.action import Action

from client import HockeyClient, ClientFactory

class StupidClient(HockeyClient):
    def move(self):
        if self.goal == -1:
            if self.X < 0 and self.Y < 0:
                return Action.to_number("north east")
            if self.Y == 0 and self.X < 0:
                return Action.to_number("south east")
            if self.Y == 0 and self.X > 0:
                return Action.to_number("south west")
            if self.Y > 0 and self.X > 0:
                return Action.to_number("north west")
            if self.X == 0:
                return Action.to_number("north")
        else:
            if self.X < 0 and self.Y < 10:
                return Action.to_number("south east")
            if self.Y == 10 and self.X < 0:
                return Action.to_number("north east")
            if self.Y == 10 and self.X > 0:
                return Action.to_number("north west")
            if self.Y > 10 and self.X > 0:
                return Action.to_number("south west")
            if self.X == 0:
                return Action.to_number("south")

        return Action.to_number("south")

class StupidClientFactory(ClientFactory):
    def __init__(self, debug):
        self.name =  "Canadian Immigrants"
        self.debug = debug

    def buildProtocol(self, addr):
        return StupidClient(self.name, self.debug)



