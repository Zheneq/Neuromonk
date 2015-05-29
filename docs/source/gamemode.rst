.. Neuroshima Hex documentation master file, created by
   sphinx-quickstart on Thu May 28 23:52:06 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

GameMode
========

This is the main module of the project. It contains the essence of the game process. API of GameMode is represented by 2 classes: :py:class:`src.game.gamemode.GameMode()` and :py:class:`src.game.gamemode.Neuroshima()`. Former, :py:class:`src.game.gamemode.GameMode()`, implements abstract board game logic while latter, :py:class:`src.game.gamemode.Neuroshima()`, is inherited from the former one and determines details of Neurshima Hex game process.


GameMode API
============
.. automodule:: src.game.gamemode
   :members:
