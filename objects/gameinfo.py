from objects.players import Player, EnemyAI
from settings import SCREEN_HEIGHT, SCREEN_WIDTH

import pygame as pg
from icecream import ic


class GameInfo:
    def __init__(self) -> None:
        self.font = pg.font.Font(None, 24)

    # Set up players and all sprite groups
    def startup(self) -> None:
        pass

    # Update all objects
    def update(self) -> None:
        pass

    # Draw background
    def draw(
        self,
        surface,
        p1,
        p1_health,
        p1_energy,
        p2,
        p2_health,
        p2_energy,
    ) -> None:

        p1_text1 = self.font.render(f"{p1}", True, (255, 255, 255))
        p1_text2 = self.font.render(f"{p1_health}", True, (255, 255, 255))
        p1_text3 = self.font.render(f"{p1_energy}", True, (255, 255, 255))
        p2_text1 = self.font.render(f"{p2}", True, (255, 255, 255))
        p2_text2 = self.font.render(f"{p2_health}", True, (255, 255, 255))
        p2_text3 = self.font.render(f"{p2_energy}", True, (255, 255, 255))

        surface.blit(p1_text1, ((int(SCREEN_WIDTH * 0.15), int(SCREEN_HEIGHT * 0.92))))
        surface.blit(p1_text2, ((int(SCREEN_WIDTH * 0.15), int(SCREEN_HEIGHT * 0.95))))
        surface.blit(p1_text3, ((int(SCREEN_WIDTH * 0.15), int(SCREEN_HEIGHT * 0.98))))
        surface.blit(p2_text1, ((int(SCREEN_WIDTH * 0.85), int(SCREEN_HEIGHT * 0.92))))
        surface.blit(p2_text2, ((int(SCREEN_WIDTH * 0.85), int(SCREEN_HEIGHT * 0.95))))
        surface.blit(p2_text3, ((int(SCREEN_WIDTH * 0.85), int(SCREEN_HEIGHT * 0.98))))
