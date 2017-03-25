import random

from twisted.internet import protocol
from twisted.internet import reactor
from twisted.protocols.basic import LineReceiver

from hockey.action import Action

from client import HockeyClient, ClientFactory
import random
import re


class StupidClient(HockeyClient):
    def __init__(self, name, debug):
        self.name = name
        self.debug = debug
        self.X = 7
        self.Y = 7

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
        elif 'polarity of the goal has been inverted' in line:
            self.goal = 15 if self.goal == -1 else -1
        elif 'did go' in line:
            d1 = line.split(' ')[-4]
            d2 = line.split(' ')[-3]
            if d1 == 'north' or d2 == 'north':
                self.Y -= 1
            if d1 == 'south' or d2 == 'south':
                self.Y += 1
            if d2 == 'east':
                self.X += 1
            if d2 == 'west':
                self.X -= 1


        elif 'your goal is' in line:
            if 'north' in line:
                self.goal = -1
            else:
                self.goal = 15

    def move_random(self):
         return Action.from_number(random.randint(0, 7))

    def play_random(self):
        result = self.move_random()
        self.sendLine(result)

    def move(self):
        if self.goal == -1:
            if self.X < 7 and self.Y > 0:
                return "north east"
            if self.Y == 0 and self.X < 7:
                return "south east"
            if self.Y == 0 and self.X > 7:
                return "south west"
            if self.Y > 0 and self.X > 7:
                return "north west"
            if self.X == 7:
                return "north"
        else:
            if self.X < 7 and self.Y < 14:
                return "south east"
            if self.Y == 14 and self.X < 7:
                return "north east"
            if self.Y == 14 and self.X > 7:
                return "north west"
            if self.Y < 14 and self.X > 7:
                return "south west"
            if self.X == 7:
                return "south"


class StupidClientFactory(ClientFactory):
    def __init__(self, debug):
        self.name =  "Canadian Immigrants2"
        self.debug = debug

    def buildProtocol(self, addr):
        return StupidClient(self.name, self.debug)



