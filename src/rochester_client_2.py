import random
import sys

from twisted.internet import protocol
from twisted.internet import reactor
from twisted.protocols.basic import LineReceiver

from hockey.action import Action
from hockey.controller import *

from client import HockeyClient, ClientFactory

class UndoLegalMove(RuleEnforcer):
    def apply_rule(self, action):
        del self.controller.actions[-1]
        x, y = self.controller.ball
        ball_x, ball_y = self._get_ball_destination(self._opposite_action(action))

        self.controller.dots[ball_x][ball_y]['actions'][action] = False
        self.controller.dots[x][y]['actions'][self._opposite_action(action)] = False
        # update bounce
        bounceball = False
        for action in self.controller.dots[bx][by]['actions']:
            if self.controller.dots[bx][by]['actions'][action]:
                bounceball = True
        if not bounceball:
            self.controller.dots[bx][by]['bounce'] = False

        bouncereg = False
        for action in self.controller.dots[x][y]['actions']:
            if self.controller.dots[x][y]['actions'][action]:
                bouncereg = True
        if not bouncereg:
            self.controller.dots[x][y]['bounce'] = False

        if not self.controller.dots[bx][by]['bounce']:
            self.controller._switch_player()

        self.controller.ball = (bx, by)
        self.controller.dots[x][y]['bounce'] = True

    def _opposite_action(self, action):
        return Action.from_number((Action.to_number(action) + 4) % 8)




class RochesterClient(HockeyClient):
    def __init__(self, name, debug):
        size_x = 11
        size_y = 11
        self.size_x = size_x
        self.size_y = size_y
        self.name = name
        self.debug = debug
        self.X = 5
        self.Y = 5
        self.actions = []
        self.ball = int(round(math.ceil(size_x / 2.0) - 1, 0)), int(round(math.ceil(size_y / 2.0) - 1, 0))
        self.dots = BoardBuilder.init(self.size_x, self.size_y)
        self.dots[self.ball[0]][self.ball[1]]['bounce'] = True
        self.controller = RochesterController()
        self.depth = 5

    def apply_move(self, action):
        return self.controller.move(action)

    def undo_move(self, action):
        self.controller.undo_move(action)

    def move(self):
        # iterative deepening 
        best_move = self.iterative_deepening()
        return Action.from_number(best_move)
        #return Action.from_number(0)

    def iterative_deepening(self):
        actions = self.controller.get_possible_actions(self.controller.ball[0], self.controller.ball[1])
        value = -10000000
        best_action = random.randint(0, 7)
        for action in actions:
            newvalue = self.idrec(0, self.controller.active_player)
            if newvalue > value:
                value = newvalue
                best_action = action
        return best_action

    def idrec(self, depth, player):
        best_move = None
        if depth >= self.depth:
            return self.heuristic()
        actions = self.controller.get_possible_actions(self.controller.ball[0], self.controller.ball[1])
        best_heuristic = -10000000
        if self.us != player:
            best_heuristic = 10000000
        for action in actions:
            oldplayer = self.controller.active_player
            action_result = self.apply_move(action)
            if action_result.terminated:
                if self.us != player:
                    best_heuristic = min(best_heuristic, self.heuristic())
                else:
                    best_heuristic = max(best_heuristic, self.heuristic())
            if oldplayer != self.controller.active_player:
                depth += 1
            if self.us != player:
                best_heuristic = min(best_heuristic, self.idrec(depth, self.controller.active_player))
            else:
                best_heuristic = max(best_heuristic, self.idrec(depth, self.controller.active_player))
        return best_heuristic


    def heuristic(self):
        if self.controller.terminated:
            if int(self.winner) == self.us:
                return 100000
            else:
                return -100000
        # stub
        return random.randint(-10, 10)




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
        self.players = ["0", "1"]
        self.active_player = 0
        self.terminated = False
        self.printer = printer()

        next_rule = self.rule()

        self.rule_chain = next_rule
        self.undo_rule_chain = self.undorule()

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

    def undorule(self):
        next_rule = UndoLegalMove(self, None)
        return next_rule

    def move(self, action):
        id = (self.active_player + 1) % 2
        action_result = self.rule_chain.process(action)
        if action_result.terminated:
            if self.ball[1] == self.goal_by_player[0]:
                action_result.winner = self.players[0]
                self.winner = self.players[0]
            elif self.ball[1] == self.goal_by_player[1]:
                action_result.winner = self.players[1]
                self.winner = self.players[1]
            elif len(self.get_possible_actions(self.ball[0], self.ball[1])) == 0:
                action_result.winner = self.players[id]
                self.winner = self.players[id]
        return action_result

    def undo_move(self, action):
        id = (self.active_player + 1) % 2
        action_result = self.undo_rule_chain.process(action)
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
