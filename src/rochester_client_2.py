import random
import sys
import json
import math

from twisted.internet import protocol
from twisted.internet import reactor
from twisted.protocols.basic import LineReceiver

from hockey.action import Action
from hockey.controller import *
from hockey2.controller_polarity import *

from client import HockeyClient, ClientFactory

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



def obj_equals(a, b):
    if not a and not b:
        return True
    if not a or not b:
        return False
    if type(a) != type(b):
        return False
    if type(a) is object:
        if a.keys() != b.keys():
            return False
        for k in a.keys():
            if not obj_equals(a[k], b[k]):
                return False
        return True
    return a == b

class ApplyLegalMove(RuleEnforcer):
    def apply_rule(self, action):
        self.controller.actions.append((self.controller.ball, self.controller.active_player, action))
        ball_x, ball_y = self.controller.ball
        x, y = self._get_ball_destination(action)
        if not self.controller.dots[x][y]['bounce']:
            self.controller._switch_player()

        self.controller.ball = (x, y)

        self.controller.dots[ball_x][ball_y]['actions'][action] = True
        self.controller.dots[x][y]['actions'][self._opposite_action(action)] = True

        self.controller.dots[x][y]['bounce'] = True
        if self.controller.dots[x][y]['is_goal']:
            result = ActionResults(self.controller.active_player_name(), terminated=True, reason="a goal was made")
        else:
            result = ActionResults(self.controller.active_player_name(), terminated=False)
            if len(self.controller.get_possible_actions(x, y)) == 0:
                self.controller._switch_player()
                result = ActionResults(self.controller.active_player_name(), terminated=True,
                                       reason="checkmate was achieved")
        return result

    def _opposite_action(self, action):
        return Action.from_number((Action.to_number(action) + 4) % 8)


class UndoLegalMove(RuleEnforcer):
    def __init__(self, controller, next_rule):
        self.controller = controller
        self.next_rule = next_rule

    def apply_rule(self, action):
        print('undoing things', action)
        assert action == self.controller.actions[-1][2]
        saved_action = self.controller.actions[-1]
        del self.controller.actions[-1]
        x, y = self.controller.ball
        ball_x, ball_y = self._get_ball_destination(self._opposite_action(action))

        self.controller.dots[ball_x][ball_y]['actions'][action] = False
        self.controller.dots[x][y]['actions'][self._opposite_action(action)] = False
        # previous position
        bounceball = False
        edgecounter = 0
        for action in self.controller.dots[ball_x][ball_y]['actions']:
            if self.controller.dots[ball_x][ball_y]['actions'][action]:
                bounceball = True
                edgecounter += 1
        if not bounceball:
            self.controller.dots[ball_x][ball_y]['bounce'] = False

        # undo position (now in future)
        bouncereg = False
        opencounter = 0
        for action in self.controller.dots[x][y]['actions']:
            if self.controller.dots[x][y]['actions'][action]:
                bouncereg = True
            else:
                opencounter += 1
        if not bouncereg:
            self.controller.dots[x][y]['bounce'] = False

        #if edgecounter <= 1:
            #self.controller._switch_player()
        #if opencounter == 1:
            #self.controller._switch_player()

        self.controller.ball = (ball_x, ball_y)

        self.terminated = False

        #if len(self.controller.actions) >= 1:
            #self.controller.active_player = self.controller.actions[-1][1]
        #else:
            #self.controller.active_player = 0
        self.controller.active_player = saved_action[1]

        #print('finishing undo', self.controller.actions, self.controller.active_player)

        return ActionResults(self.controller.active_player_name(), terminated=False)


    def _opposite_action(self, action):
        return Action.from_number((Action.to_number(action) + 4) % 8)




class RochesterClient(HockeyClient):
    def __init__(self, name, debug, heuristic="diagonal"):
        size_x = 15
        size_y = 15
        self.size_x = size_x
        self.size_y = size_y
        self.name = name
        self.debug = debug
        self.X = 7
        self.Y = 7
        self.actions = []
        self.ball = int(round(math.ceil(size_x / 2.0) - 1, 0)), int(round(math.ceil(size_y / 2.0) - 1, 0))
        self.dots = BoardBuilder.init(self.size_x, self.size_y)
        self.dots[self.ball[0]][self.ball[1]]['bounce'] = True
        self.controller = RochesterController()
        self.depth = 1
        self.powerX = -1
        self.powerY = -1
        self.powerupUsed = False
        self.havePowerup = False
        self.powerupCaptured = False
        self.heuristicType = heuristic
        self.heuristic_to_range = {
                'eculidean': 10,
                'manhattan': 22,
                'diagonal': 25,
                'possible_actions': 128,
        }

        self.heuristic_to_function = {
            'eculidean': self.eculidean_heuristic,
            'manhattan': self.manhattan_heuristic,
            'diagonal': self.diagonal_heuristic,
            'possible_actions': self.possible_actions_heuristic,
        }

        self.weights = [0 for x in range(len(self.heuristic_to_range.keys())]

        self.lastMove = None
        self.lastMoveInvalid = False
        self.triedPower = False

        self.debugcounter = 0

    def parse_didgo(self, line):
        super(RochesterClient, self).parse_didgo(line)
        self.apply_move(self.news)

    def parsePowerUpAt(self, line):
        super(RochesterClient, self).parsePowerUpAt(line)
        self.controller.power_up_position = [self.powerX, self.powerY]

    def apply_move(self, action):
        move = self.controller.move(action)
        self.saved_active_player = self.controller.active_player
        return move

    def undo_move(self, action):
        self.controller.undo_move(action)

    def move(self):
        #print('moving...', self.us, self.controller.active_player)
        #assert self.us == self.controller.active_player
        # just in case, sometimes fails
        if self.us != self.controller.active_player:
            print('NOT ACTIVE PLAYER... STATE MAY HAVE BEEN CORRUPTED')
            self.controller.active_player = self.us
        # check for invalid
        if self.lastMoveInvalid and self.triedPower:
            self.triedPower = False
            print('last invalid', self.lastMove)
            return self.lastMove
        # iterative deepening 
        olddots = copy.deepcopy(self.dots)
        #print(json.dumps(olddots))
        best_move, best_heuristic = self.iterative_deepening()
        #print('iterative deepening returns', best_move, best_heuristic)
        #print(json.dumps(self.dots))
        assert obj_equals(self.dots, olddots)
        #print('consistency check', self.controller.ball, self.X, self.Y)
        #assert self.controller.ball[0] == self.X
        #assert self.controller.ball[1] == self.Y
        self.lastMove = best_move
        self.triedPower = True
        if self.lastMoveInvalid:
            # trouble
            print('STATE MIGHT BE CORRUPTED')
            return Action.from_number(random.randint(0, 7))
        print('moving power ' + best_move)
        return "power " + best_move
        #return Action.from_number(0)

    def iterative_deepening(self):
        action, value = self.idrec(0, self.controller.active_player)
        return action, value

    def idrec(self, depth, player):
        self.debugcounter += 1
        #if self.debugcounter >= 50:
            #assert False
        #print('calling idrec', depth, player, self.controller.ball)
        best_move = None
        if depth >= self.depth:
            sheur = self.heuristic()
            #print('idrec returns', None, sheur)
            return None, sheur
        actions = self.controller.get_possible_actions(self.controller.ball[0], self.controller.ball[1])
        #print('actions are', actions)
        #print(actions)
        best_heuristic = -10000000
        if self.us != player:
            best_heuristic = 10000000
        for action in actions:
            #print('action:', action)
            oldplayer = self.controller.active_player
            action_result = self.apply_move(action)
            if action_result.terminated:
                sheur = self.heuristic()
                if self.us != player:
                    if sheur < best_heuristic:
                        best_heuristic = sheur
                        best_move = action
                else:
                    if sheur > best_heuristic:
                        best_heuristic = sheur
                        best_move = action
            newdepth = depth
            if oldplayer != self.controller.active_player:
                newdepth += 1
            #print('depths:', depth, newdepth)
            actcopy, rec = self.idrec(depth+1, self.controller.active_player)
            if self.us != player:
                if rec < best_heuristic:
                    best_heuristic = rec
                    best_move = action
            else:
                if rec > best_heuristic:
                    best_heuristic = rec
                    best_move = action
            self.undo_move(action)
            #print('player check', oldplayer, self.controller.active_player)
            assert oldplayer == self.controller.active_player
        #print('idrec returns', best_move, best_heuristic)
        return best_move, best_heuristic


    def heuristic(self):
        if self.controller.terminated:
            if int(self.winner) == self.us:
                return 100000
            else:
                return -100000
        if self.heuristicType == "manhattan":
            return self.manhattan_heuristic()
        elif self.heuristicType == "diagonal":
            return self.diagonal_heuristic()
        elif self.heuristicType == "powerup":
            return self.powerup_heuristic()
        elif self.heuristicType == "possibleactions":
            return self.possible_actions_heuristic()
        elif self.heuristicType == "combined":
            return self.combine_heuristics()
        else:
            print('NO HEURISTIC...')
            return 0

    def manhattan_heuristic(self):
        dist = abs(self.controller.ball[0] - 7) + abs(self.controller.ball[1] - self.goal)
        return 7 - dist

    def diagonal_heuristic(self):
        diff1 = abs(self.controller.ball[0] - 7)
        diff2 = abs(self.controller.ball[1] - self.goal)
        m = max(diff1, diff2)
        d = abs(diff1 - diff2)
        return 7 - (m + d)

    def eculidean_heuristic(self):
        posX = self.controller.ball[0]
        posY = self.controller.ball[1]

        return math.sqrt(abs(posX - 7) * abs(posX - 7) + abs(posY - self.goal)*abs(posY - self.goal))


    def possible_actions_heuristic(self):
        posX = self.controller.ball[0]
        posY = self.controller.ball[1]
        x = posX
        y = posY
        num_actions = 0
        actions = self.controller.get_possible_actions(posX, posY)
        for action in actions:
            x += string_to_diff[action][0]
            y += string_to_diff[action][1]
            num_actions += len(self.controller.get_possible_actions(x, y))
            x = posX
            y = posY

        return num_actions if self.us == self.controller.active_player else -num_actions


    def powerup_heuristic(self):
        dist = abs(self.controller.ball[0] - self.controller.power_up_position[0]) + abs(self.controller.ball[1] - self.controller.power_up_position[1])
        return 7 - dist

    def combine_heuristics(self):
        value = 0
        if  len(self.heuristic_to_range.keys()) != len(self.weights):
            return value
        for h, w in zip(self.heuristic_to_range.keys(), self.weights):
            if (self.heuristic_to_range[n] is None or self.heuristic_to_function[h] is None):
                continue
            value += (self.heuristic_to_function[h](self)/self.heuristic_to_range[h]) * w

        return value

    def setWeights(self, weights):
        self.weights = weights



class RochesterController(Controller):
    def __init__(self, size_x=15, size_y=15, builder=BoardBuilder, printer=BoardPrinterCurrent):
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
        self.power_up = None
        self.power_up_position = [-1, -1]

        self.powerUsed = False
        self.hasPower = None

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
        power_up = True if "power" in action and self.power_up == self.active_player else False
        if "power" in action:
            action = action.split(' ')[1]
        initial_active = self.active_player
        #print('moving', action, self.ball)
        id = (self.active_player + 1) % 2
        action_result = self.rule_chain.process(action)

        if self.ball[0] == self.power_up_position[0] and self.ball[1] == self.power_up_position[1]:
            self.power_up = initial_active

        if power_up:
            self.power_up = None
            self.active_player = initial_active 

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
        #print('moved: ', action, self.ball)
        return action_result

    def undo_move(self, action):
        id = (self.active_player + 1) % 2
        action_result = self.undo_rule_chain.process(action)
        #print('another check', self.active_player)
        return action_result

    def _switch_player(self):
        self.active_player += 1
        self.active_player %= 2

    def register(self, player_name):
        self.players.append(player_name)

    def get_possible_actions(self, x, y):
        place = self.dots[x][y]['actions']

        acts = [action for action in place if not place[action]]
        #print(acts)
        return acts

class RochesterClientFactory(ClientFactory):
    def __init__(self, debug, heuristic="diagonal"):
        self.debug = debug
        self.heuristic = heuristic
        # TODO: CHANGE BEFORE SUBMITTING
        self.name =  "Canadian Immigrants"+self.heuristic

    def buildProtocol(self, addr):
        return RochesterClient(self.name, self.debug, heuristic=self.heuristic)


