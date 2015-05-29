.. Neuroshima Hex documentation master file, created by
   sphinx-quickstart on Thu May 28 23:52:06 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Tile
====

This module contains almost all visible entities related directly to the game process in Neuroshima. These entities are `Soldiers`, `Modules`, 'Orders', etc. They are units each player controls and actions each player can use to bring his army to win.

The base class :py:class:`src.game.common.tile.Hex()` combines information that have all these entities (such as membership in particular army oa name of entity). Then there are two classes :py:class:`src.game.common.tile.Tile()` and :py:class:`src.game.common.tile.Order()`, inherited from the `Hex()` class. `Order` is an action type player can use during his turn to influence in some way the gameboard while `Tile` is every object that can be placed to the board. After that there are 2 more classes :py:class:`src.game.common.tile.Unit()` and :py:class:`src.game.common.tile.Module()`, inherited from `Tile()` class. `Unit` is every object that can perform some actions (itself or caused by player's `Order()`) while `Module` is passive tile, giving some bonuses to nearby allies and cursing nearby enemies. Also there is :py:class:`src.game.common.tile.DisposableModule()`, inherited from `Module()` and is Module that grants bonuses and/or curses only once per player's turn. At the end of hierarchy is :py:class:`src.game.common.tile.Base()`, inherited both from `Tile()` and `Module()`. This tile is unique for every player and represents the player's Headquarters. If a player loses his HQ he loses the game.


Tile API
============
.. automodule:: src.game.common.tile
   :members:
