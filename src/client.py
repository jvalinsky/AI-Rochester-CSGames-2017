import random
import re

from twisted.internet import protocol
from twisted.internet import reactor
from twisted.protocols.basic import LineReceiver

from hockey.action import Action


class HockeyClient(LineReceiver, object):
    def __init__(self, name, debug):
        self.name = name
        self.debug = debug
        self.X = 5
        self.Y = 5

    def connectionMade(self):
        self.sendLine(self.name)

    def sendLine(self, line):
        super(HockeyClient, self).sendLine(line.encode('UTF-8'))

    def lineReceived(self, line):
        line = line.decode('UTF-8')
        if self.debug:
            print('Server said:', line)
        if '{} is active player'.format(self.name) in line or 'invalid move' in line:
            self.play_game()
        elif 'ball is at' in line:
            nums = re.findall(r'\d+', line)
            self.X = int(nums[0])
            self.Y = int(nums[1])
        elif 'your goal is' in line:
            if 'north' in line:
                self.goal = -1
            else:
                self.goal = 11

    def play_game(self):
        result = self.move()
        self.sendLine(result)

    def move(self):
        return Action.from_number(random.randint(0, 7))



class ClientFactory(protocol.ClientFactory):
    def __init__(self, name, debug):
        self.name = name
        self.debug = debug

    def buildProtocol(self, addr):
        return HockeyClient(self.name, self.debug)

    def clientConnectionFailed(self, connector, reason):
        if self.debug:
            print("Connection failed - goodbye!")
        reactor.stop()

    def clientConnectionLost(self, connector, reason):
        if self.debug:
            print("Connection lost - goodbye!")
        reactor.stop()


name = "Canadian Immigrants"

f = ClientFactory(name, debug=True)
reactor.connectTCP("localhost", 8023, f)
reactor.run()
