from twisted.internet import protocol
from twisted.internet import reactor
from twisted.protocols.basic import LineReceiver

from hockey.action import Action

from rochester_client_2 import *

def main():
    f = RochesterClientFactory(debug=True, heuristic="manhattan")
    reactor.connectTCP("localhost", 8023, f)
    reactor.run()


if __name__ == "__main__":
    main()
