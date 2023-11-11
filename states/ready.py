from .base import BaseState
from objects.ship import Ship
from settings import SCREEN_HEIGHT, SCREEN_WIDTH
from icecream import ic

import pygame as pg


class Ready(BaseState):
    def __init__(self) -> None:
        super().__init__()
        self.active_index = 0
        self.options = ["Start Game Player vs AI", "Start Game Player vs Player", "Quit Game"]
        self.name = "READY"
        self.next_state = "GAMEPLAY"
        self.font_large = pg.font.Font("assets/fonts/spacegame/Space Game.ttf", size=72)
        self.font = pg.font.Font("assets/fonts/spacegame/Space Game.ttf", size=48)
        self.font_small = pg.font.Font("assets/fonts/spacegame/Space Game.ttf", size=24)
        self.color_change = 10
        self.gray_tone = 128

    def startup(self, fight_status) -> None:
        self.fight_status = fight_status

        y_pos = int(SCREEN_HEIGHT * 0.4)
        height = 128
        width = height

        x1_pos = int(SCREEN_WIDTH * 0.25)
        x2_pos = SCREEN_WIDTH - x1_pos

        center_x1 = x1_pos + width / 2
        center_x2 = x2_pos + width / 2 - width

        center_y1 = center_y2 = y_pos + height / 2

        ship1 = Ship(center_x1, center_y1, 180, 0, 180, self.fight_status.p1_ship)
        ship2 = Ship(center_x2, center_y2, 180, 0, 180, self.fight_status.ai_ship)
        self.ship_group = pg.sprite.Group()

        self.ship_group.add(ship1)
        self.ship_group.add(ship2)

    def get_event(self, event) -> None:
        if event.type == pg.QUIT:
            self.quit = True
        elif event.type == pg.KEYUP:
            if event.key == pg.K_SPACE:
                self.done = True
                pg.mixer.stop()
            elif event.key == pg.K_ESCAPE:
                self.quit = True
                pg.mixer.stop()

    def draw_ships(self, surface) -> None:
        y_pos = int(SCREEN_HEIGHT * 0.4)
        height = 128
        width = height

        x1_pos = int(SCREEN_WIDTH * 0.25)
        x2_pos = SCREEN_WIDTH - x1_pos

        pg.draw.rect(surface, pg.Color("white"), pg.Rect(x1_pos, y_pos, height, width))
        pg.draw.rect(surface, pg.Color("white"), pg.Rect(x2_pos - width, y_pos, height, width))

        pg.draw.rect(
            surface, pg.Color("black"), pg.Rect(x1_pos + 10, y_pos + 10, height - 20, width - 20)
        )
        pg.draw.rect(
            surface,
            pg.Color("black"),
            pg.Rect(x2_pos + 10 - width, y_pos + 10, height - 20, width - 20),
        )

        self.ship_group.update()
        self.ship_group.draw(surface)

    def draw(self, surface) -> None:
        middle = int(SCREEN_WIDTH / 2)

        surface.fill(pg.Color("black"))

        self.draw_ships(surface)

        p1_lead = 0
        ai_lead = 0

        if self.fight_status.p1_wins > self.fight_status.ai_wins:
            p1_lead = self.fight_status.p1_wins - self.fight_status.ai_wins
        elif self.fight_status.p1_wins < self.fight_status.ai_wins:
            ai_lead = self.fight_status.ai_wins - self.fight_status.p1_wins

        text_top = self.font_large.render(f"Ready?", True, pg.Color("white"))
        text_top_x = int(SCREEN_WIDTH / 2) - int(text_top.get_width() / 2)
        text_top_y = int(SCREEN_HEIGHT * 0.3)

        text_wins = self.font.render(
            f"WINS:          {self.fight_status.p1_wins}                    {self.fight_status.ai_wins}",
            True,
            pg.Color("white"),
        )
        text_wins_x = int(SCREEN_WIDTH / 2) - int(text_wins.get_width() / 2 + SCREEN_WIDTH * 0.12)
        text_wins_y = int(SCREEN_HEIGHT * 0.6)

        text_lead = self.font.render(
            f"LEAD:          {p1_lead}                    {ai_lead}",
            True,
            pg.Color("white"),
        )
        text_lead_x = int(SCREEN_WIDTH / 2) - int(text_wins.get_width() / 2 + SCREEN_WIDTH * 0.124)
        text_lead_y = int(SCREEN_HEIGHT * 0.65)

        text_explainer = self.font.render(
            f"FIRST TO 10 WINS OR LEADING BY 3 WINS!", True, pg.Color("white")
        )

        self.gray_tone += self.color_change
        if self.gray_tone >= 255 - self.color_change or self.gray_tone + self.color_change <= 0:
            self.color_change *= -1

        text_continue = self.font_small.render(
            f"PRESS SPACE TO CONTINUE OR ESC TO EXIT",
            True,
            pg.Color(self.gray_tone, self.gray_tone, self.gray_tone),
        )

        surface.blit(text_top, (text_top_x, text_top_y))
        surface.blit(text_wins, (text_wins_x, text_wins_y))
        surface.blit(text_lead, (text_lead_x, text_lead_y))
        surface.blit(
            text_explainer,
            (
                (
                    middle - int(text_explainer.get_width()) / 2,
                    (int(SCREEN_HEIGHT * 0.8)),
                )
            ),
        )
        surface.blit(
            text_continue,
            (
                (
                    middle - int(text_continue.get_width()) / 2,
                    (int(SCREEN_HEIGHT * 0.9)),
                )
            ),
        )
