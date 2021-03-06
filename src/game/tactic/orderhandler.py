__author__ = 'dandelion'

from src.game.tactic.orders.march import March
from src.game.tactic.orders.pushback import PushBack
from src.game.tactic.orders.airstrike import AirStrike
from src.game.tactic.orders.grenade import Grenade
from src.game.tactic.orders.sniper import Sniper


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
        print '\t' + self.game.player.name, 'applies', order.type, 'order'
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
