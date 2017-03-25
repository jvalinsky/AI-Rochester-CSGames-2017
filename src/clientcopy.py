import random
import re

from twisted.internet import protocol
from twisted.internet import reactor
from twisted.protocols.basic import LineReceiver

from hockey.action import Action

string_to_diff = {
        'north': (0, -1),
        'north east': (1, -1),
        'east': (1, 0),
        'south east': (1, 1),
        'south': (0, 1),
        'south west': (-1, 1),
        'west': (-1, 0),
        'north west': (-1, -1),
}

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
        elif "you're player" in line:
            nums = re.findall(r'\d+', line)
            self.us = int(nums[-1])
        elif 'ball is at' in line:
            nums = re.findall(r'\d+', line)
            self.X = int(nums[0])
            self.Y = int(nums[1])
        elif 'did go' in line:
            self.parse_didgo(line)
        elif 'your goal is' in line:
            if 'north' in line:
                self.goal = -1
            else:
                self.goal = 11

    def parse_didgo(self, line):
        sp = line.split(" ")
        if sp[-4] == 'north' or sp[-4] == 'south':
            news = sp[-4] + " " + sp[-3]
        else:
            news = sp[-3]
        s2d = string_to_diff[news]
        self.X += s2d[0]
        self.Y += s2d[1]



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



def main():
    name = "Bob{}".format(random.randint(0, 999))

    f = ClientFactory(name, debug=True)
    reactor.connectTCP("localhost", 8023, f)
    reactor.run()


if __name__ == "__main__":
    main()
