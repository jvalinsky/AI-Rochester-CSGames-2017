import random

from twisted.internet import protocol
from twisted.internet import reactor
from twisted.protocols.basic import LineReceiver

from hockey.action import Action

from client import HockeyClient, ClientFactory
import random
import re


class StupidClient(HockeyClient):

    def lineReceived(self, line):
        line = line.decode('UTF-8')
        if self.debug:
            print('Server said:', line)
        if '{} is active player'.format(self.name) in line:
            self.play_game()
        elif 'invalid move' in line:
            self.play_random()
        elif 'ball is at' in line:
            nums = re.findall(r'\d+', line)
            self.X = int(nums[0])
            self.Y = int(nums[1])
        elif 'your goal is' in line:
            if 'north' in line:
                self.goal = -1
            else:
                self.goal = 11

    def move_random(self):
         return Action.from_number(random.randint(0, 7))

    def play_random(self):
        result = self.move_random()
        self.sendLine(result)

    def move(self):
        if self.goal == -1:
            if self.X < 5 and self.Y > 0:
                return "north east"
            if self.Y == 0 and self.X < 5:
                return "south east"
            if self.Y == 0 and self.X > 5:
                return "south west"
            if self.Y > 0 and self.X > 5:
                return "north west"
            if self.X == 5:
                return "north"
        else:
            if self.X < 5 and self.Y < 10:
                return "south east"
            if self.Y == 10 and self.X < 5:
                return "north east"
            if self.Y == 10 and self.X > 5:
                return "north west"
            if self.Y < 10 and self.X > 5:
                return "south west"
            if self.X == 5:
                return "south"

        return "south"

class StupidClientFactory(ClientFactory):
    def __init__(self, debug):
        self.name =  "Canadian Immigrants"
        self.debug = debug

    def buildProtocol(self, addr):
        return StupidClient(self.name, self.debug)



