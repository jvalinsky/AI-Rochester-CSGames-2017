import random
import sys

from twisted.internet import protocol
from twisted.internet import reactor
from twisted.protocols.basic import LineReceiver

from hockey.action import Action
from hockey.controller import *

from client import HockeyClient, ClientFactory

class RochesterClient(HockeyClient):
    def __init__(self, name, debug):
        self.size_x = 11
        self.size_y = 11
        self.name = name
        self.debug = debug
        self.X = 5
        self.Y = 5
        self.actions = []
        self.ball = int(round(math.ceil(size_x / 2.0) - 1, 0)), int(round(math.ceil(size_y / 2.0) - 1, 0))
        self.dots = BoardBuilder.init(self.size_x, self.size_y)
        self.dots[self.ball[0]][self.ball[1]]['bounce'] = True
        self.controller = RochesterController()

    def move(self):
        print(self.dots)
        return Action.from_number(0)


class RochesterController(Controller):
    def __init__(self, size_x=11, size_y=11, builder=BoardBuilder, printer=BoardPrinterCurrent):
        self.actions = []
        self.ball = int(round(math.ceil(size_x / 2.0) - 1, 0)), int(round(math.ceil(size_y / 2.0) - 1, 0))
        self.size_x = size_x
        self.size_y = size_y
        self.goal_by_player = (-1, self.size_y)
        self.dots = builder.init(self.size_x, self.size_y)
        self.initial_dots = copy.deepcopy(self.dots)
        self.dots[self.ball[0]][self.ball[1]]['bounce'] = True
        self.players = []
        self.active_player = 0
        self.terminated = False
        self.printer = printer()

        next_rule = self.rule()

        self.rule_chain = next_rule

    def active_player_name(self):
        return self.players[self.active_player]

    def in_active_player_name(self):
        return self.players[(self.active_player + 1) % 2]

    def rule(self):
        next_rule = NoRuleEnforcerFound(self, None)
        next_rule = ApplyLegalMove(self, next_rule)
        next_rule = IllegalMove(self, next_rule)
        next_rule = OutOfBound(self, next_rule)
        next_rule = GameTerminated(self, next_rule)
        return next_rule

    def move(self, action):
        id = (self.active_player + 1) % 2
        action_result = self.rule_chain.process(action)
        if action_result.terminated:
            if self.ball[1] == self.goal_by_player[0]:
                action_result.winner = self.players[0]
            elif self.ball[1] == self.goal_by_player[1]:
                action_result.winner = self.players[1]
            elif len(self.get_possible_actions(self.ball[0], self.ball[1])) == 0:
                action_result.winner = self.players[id]
        return action_result

    def _switch_player(self):
        self.active_player += 1
        self.active_player %= 2

    def register(self, player_name):
        self.players.append(player_name)

    def get_possible_actions(self, x, y):
        place = self.dots[x][y]['actions']

        return [action for action in place if not place[action]]




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
