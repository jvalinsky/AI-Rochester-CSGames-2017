import random

from twisted.internet import protocol
from twisted.internet import reactor
from twisted.protocols.basic import LineReceiver

from hockey.action import Action

from client import HockeyClient, ClientFactory

class StupidClient(HockeyClient):

    def lineReceived(self, line):
        line = line.decode('UTF-8')
        if self.debug:
            print('Server said:', line)
        if '{} is active player'.format(self.name) in line:
            if not ( 'invalid move' in line):
                self.invalid = False
                self.play_game()
            else:
                self.invalid = True
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
    def move(self):
        if self.invalid:
            return Action.from_number(random.randint(0, 7))
        if self.goal == -1:
            if self.X < 0 and self.Y > 0:
                return "north east"
            if self.Y == 0 and self.X < 0:
                return "south east"
            if self.Y == 0 and self.X > 0:
                return "south west"
            if self.Y > 0 and self.X > 0:
                return "north west"
            if self.X == 0:
                return "north"
        else:
            if self.X < 0 and self.Y < 10:
                return "south east"
            if self.Y == 10 and self.X < 0:
                return "north east"
            if self.Y == 10 and self.X > 0:
                return "north west"
            if self.Y < 10 and self.X > 0:
                return "south west"
            if self.X == 0:
                return "south"

        return "south"

class StupidClientFactory(ClientFactory):
    def __init__(self, debug):
        self.name =  "Canadian Immigrants"
        self.debug = debug

    def buildProtocol(self, addr):
        return StupidClient(self.name, self.debug)



