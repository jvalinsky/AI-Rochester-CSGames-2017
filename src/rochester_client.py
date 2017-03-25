import random

from twisted.internet import protocol
from twisted.internet import reactor
from twisted.protocols.basic import LineReceiver

from hockey.action import Action

from client import HockeyClient, ClientFactory

class RochesterClient(HockeyClient):
    def play_game(self):
        result = Action.from_number(random.randint(0, 7))
        self.sendLine(result)

class RochesterClientFactory(ClientFactory):
    def __init__(self, debug):
        self.name =  "Canadian Immigrants"
        self.debug = debug

    def buildProtocol(self, addr):
        return RochesterClient(self.name, self.debug)


def main():
    f = RochesterClientFactory(debug=True)
    reactor.connectTCP("localhost", 8023, f)
    reactor.run()


if __name__ == "__main__":
    main()
