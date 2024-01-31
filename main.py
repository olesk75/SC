#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import pygame as pg
from dataclasses import dataclass

from icecream import ic

from states.menu import Menu
from states.gameplay import GamePlay
from states.ready import Ready
from states.gameover import GameOver
from states.splash import Splash
from gameGL import GameGL
import settings

@dataclass()
class GameConfig:
    """
    Game configuration
    """
    FPS = settings.FPS
    SHOW_FPS = settings.SHOW_FPS
    window_size_xy = None  # only populated in GameGL

config = GameConfig

# pg setup
# Initializing
pg.mixer.pre_init(44100, -16, 2, 512)
pg.init()
pg.mixer.init()
pg.mixer.set_num_channels(16)

states = {
    "MENU": Menu(config),
    "SPLASH": Splash(config),
    "READY": Ready(config),
    "GAMEPLAY": GamePlay(config),
    "GAME_OVER": GameOver(config),
}

game = GameGL(states, "SPLASH", config)
game.run()

pg.mixer.fadeout(1000)
pg.quit()
ic("Normal exit")
sys.exit()
