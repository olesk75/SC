import pygame as pg
from icecream import ic

class Level:
    def __init__(self, number) -> None:
        self.number = number
        self.new_level(number)

    def new_level(self, number) -> None:
        ic('Instancing new level', number)
        self.number = number

    def update(self) -> None:
        pass

    def draw(self, surface) -> None:
        surface.fill(pg.Color("black"))  # Rather simple level for now

