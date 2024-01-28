import pygame as pg
from icecream import ic

from .base import BaseState
from objects.ship import Ship
from settings import SCREEN_HEIGHT, SCREEN_WIDTH


class Ready(BaseState):
    def __init__(self) -> None:
        super().__init__()
        self.active_index = 0
        self.options = ["Start Game Player vs AI", "Start Game Player vs Player", "Quit Game"]
        self.name = "READY"
        self.next_state = "GAMEPLAY"
        self.font_very_large = pg.font.Font("assets/fonts/spacegame/Space Game.ttf", size=144)
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

        self.active_effect = 0

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

        # Semi-transparent black backgrounds for the ships
        pg.draw.rect(surface, (0,0,0,128), pg.Rect(x1_pos + 10, y_pos + 10, height - 20, width - 20))
        pg.draw.rect(surface, (0,0,0,128), pg.Rect(x2_pos + 10 - width, y_pos + 10, height - 20, width - 20))

        self.ship_group.update()
        self.ship_group.draw(surface)

    def draw(self, surface, overlay) -> None:
        middle = int(SCREEN_WIDTH / 2)

        surface.fill((0,0,0,0))  # reset surface with full alpha
        self.draw_ships(surface)

        p1_lead = 0
        ai_lead = 0

        if self.fight_status.p1_wins > self.fight_status.ai_wins:
            p1_lead = self.fight_status.p1_wins - self.fight_status.ai_wins
        elif self.fight_status.p1_wins < self.fight_status.ai_wins:
            ai_lead = self.fight_status.ai_wins - self.fight_status.p1_wins

        # Preparing surfaces for blitting
            
        # Print You win/lose!
        if self.fight_status.win:
            t_result = self.font_very_large.render(f"YOU WIN!", True, pg.Color("white"))
        else:
            t_result = self.font_very_large.render(f"YOU LOSE!", True, pg.Color("white"))

        t_result_x = int(SCREEN_WIDTH / 2) - int(t_result.get_width() / 2)
        t_result_y = int(SCREEN_HEIGHT * 0.1)

        # Print Ready to go again?
        t_top = self.font.render(f"Ready to go again?", True, pg.Color("white"))
        t_top_x = int(SCREEN_WIDTH / 2) - int(t_top.get_width() / 2)
        t_top_y = int(SCREEN_HEIGHT * 0.3)

        # Print win/loss status
        t_wins = self.font.render(
            f"WINS:          {self.fight_status.p1_wins}                    {self.fight_status.ai_wins}",
            True,
            pg.Color("white"),
        )
        t_wins_x = int(SCREEN_WIDTH / 2) - int(t_wins.get_width() / 2 + SCREEN_WIDTH * 0.12)
        t_wins_y = int(SCREEN_HEIGHT * 0.6)

        # Print leader
        t_lead = self.font.render(
            f"LEAD:          {p1_lead}                    {ai_lead}",
            True,
            pg.Color("white"),
        )
        t_lead_x = int(SCREEN_WIDTH / 2) - int(t_wins.get_width() / 2 + SCREEN_WIDTH * 0.124)
        t_lead_y = int(SCREEN_HEIGHT * 0.65)

        # Print explainer
        t_explainer = self.font.render(f"FIRST TO 10 WINS OR LEADING BY 3 WINS!", True, pg.Color("white"))
        t_explainer_x = middle - int(t_explainer.get_width()) / 2
        t_explainer_y = int(SCREEN_HEIGHT * 0.8)

        self.gray_tone += self.color_change
        if self.gray_tone >= 255 - self.color_change or self.gray_tone + self.color_change <= 0:
            self.color_change *= -1

        # Print Continue?
        t_continue = self.font_small.render(
            f"PRESS SPACE TO CONTINUE OR ESC TO EXIT",
            True,
            pg.Color(self.gray_tone, self.gray_tone, self.gray_tone),
        )
        t_continue_x = middle - int(t_continue.get_width()) / 2
        t_continue_y = int(SCREEN_HEIGHT * 0.9)

        surface.blit(t_result, (t_result_x, t_result_y))
        surface.blit(t_top, (t_top_x, t_top_y))
        surface.blit(t_wins, (t_wins_x, t_wins_y))
        surface.blit(t_lead, (t_lead_x, t_lead_y))
        surface.blit(t_explainer, (t_explainer_x, t_explainer_y))
        surface.blit(t_continue, (t_continue_x, t_continue_y))
