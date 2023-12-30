#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import pygame as pg

from icecream import ic

from states.menu import Menu
from states.gameplay import GamePlay
from states.ready import Ready
from states.gameover import GameOver
from states.splash import Splash
from game import Game
import settings


FPS = 60

# pg setup
# Initializing
pg.mixer.pre_init(44100, -16, 2, 512)
pg.init()
pg.mixer.init()
pg.mixer.set_num_channels(16)


states = {
    "MENU": Menu(),
    "SPLASH": Splash(),
    "READY": Ready(),
    "GAMEPLAY": GamePlay(),
    "GAME_OVER": GameOver(),
}

game = Game(states, "SPLASH", FPS)
game.run()

pg.mixer.fadeout(1000)
pg.quit()
ic("Normal exit")
sys.exit()
