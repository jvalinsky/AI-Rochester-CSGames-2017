from twisted.internet import protocol
from twisted.internet import reactor
from twisted.protocols.basic import LineReceiver

from hockey.action import Action

from stupid_client import StupidClient, StupidClientFactory

def main():
    f = StupidClientFactory(debug=True)
    reactor.connectTCP("localhost", 8023, f)
    reactor.run()


if __name__ == "__main__":
    main()
