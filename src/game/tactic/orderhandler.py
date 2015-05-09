__author__ = 'dandelion'

from game.tactic.orders.march import March
from game.tactic.orders.pushback import PushBack
from game.tactic.orders.airstrike import AirStrike
from game.tactic.orders.grenade import Grenade
from game.tactic.orders.sniper import Sniper


class OrderHandler(object):
    """
    Handles Orders during the game
    """
    def __init__(self, game):
        self.game = game
        self.march_order = March(game)
        self.pushback_order = PushBack(game)
        self.airstrike_order = AirStrike(game)
        self.grenade_order = Grenade(game)
        self.sniper_order = Sniper(game)

    def resolve_order(self, order):
        if order.type == 'battle':
            self.game.begin_battle()
        elif order.type == 'airstrike':
            self.airstrike_order.begin_airstrike()
        elif order.type == 'grenade':
            self.grenade_order.begin_grenade()
        elif order.type == 'sniper':
            self.sniper_order.begin_sniper()
        elif order.type == 'move':
            self.march_order.begin_march()
        elif order.type == 'pushback':
            self.pushback_order.begin_pushback()
