from .base import BaseState
import pygame as pg
from objects.ship import Ship
from icecream import ic

from dataclasses import dataclass


@dataclass()
class FightStatus:
    """
    Dataclass for state of game
    """

    p1_ship: str
    ai_ship: str

    win: bool = False

    p1_wins: int = 0
    ai_wins: int = 0

class Menu(BaseState):
    def __init__(self) -> None:
        super().__init__()
        self.active_index = 0
        self.options = ["Start Game Player vs AI", "Start Game Player vs Player", "Quit Game"]
        self.name = "MENU"
        self.next_state = "GAMEPLAY"

    def startup(self, fight_status, config) -> None:
        self.fight_status = fight_status
        self.config = config

        ic(self.config)

        self.all_ships = []
        self.all_ship_sprites = pg.sprite.Group()
        self.selection_sprites = pg.sprite.Group()
        self.selected_ship = 0
        
        x_start = self.config.window_size_xy - self.config.window_size_xy * 0.8
        x_dist = int(self.config.window_size_xy * 0.8 - x_start) / len(Ship.ships)
        y = int(self.config.window_size_xy* 0.3)

        n = int(x_start)
        for ship_type in Ship.ships:
            ship_ = Ship(x_pos=n, y_pos=y, direction=0, velocity=0, heading=0, ship_type=ship_type, config=self.config)
            (x_img, y_img) = ship_.image.get_size()
            ship_.image = pg.transform.scale(ship_.image, (x_img * 2, y_img * 2))
            ship_.rect = ship_.image.get_rect()
            ship_.rect.center = (n, y)
            self.all_ships.append(ship_,)
            self.all_ship_sprites.add(ship_)
            n += x_dist

        self.update_selection_box()
            
    def update_selection_box(self) -> None:
        self.selection_sprites.empty()
        frame = 5
        size = max(self.all_ships[self.selected_ship].image.get_size())
        size += frame * 2
        background = pg.sprite.Sprite()
        background.image = pg.Surface((size, size)).convert_alpha()
        background.rect = background.image.get_rect()
        background.image.fill((255,255,255,255))
        background.image.fill((255,255,255,64), pg.Rect(frame,frame,size - frame*2, size-frame*2))
        
        background.rect.center = self.all_ships[self.selected_ship].rect.center
        self.selection_sprites.add(background)

    def render_text(self, index) -> pg.Surface:
        color = pg.Color("red") if index == self.active_index else pg.Color("white")
        return self.font.render(self.options[index], True, color)

    def get_text_position(self, text, index, surface) -> pg.Rect:
        screen_rect = surface.get_rect()
        center = (screen_rect.center[0], screen_rect.center[1] + (index * 50))
        return text.get_rect(center=center)

    def handle_action(self) -> FightStatus | None:
        if self.active_index in (0,1):
            self.done = True
            fight = FightStatus(self.all_ships[self.selected_ship].ship_type, 'rocket', False, 0,0)
            return(fight)
        elif self.active_index == 2:
            self.quit = True
            return(None)

    def get_event(self, event) -> FightStatus | None:
        if event.type == pg.QUIT:
            self.quit = True
        elif event.type == pg.KEYUP:
            if event.key == pg.K_UP:
                self.active_index -= 1 
                if self.active_index < 0:
                    self.active_index =  2
            elif event.key == pg.K_DOWN:
               self.active_index += 1 
               if self.active_index > 2:
                    self.active_index =  0

            elif event.key == pg.K_LEFT:
               self.selected_ship -= 1 
               if self.selected_ship < 0:
                    self.selected_ship = len(self.all_ships) - 1
               self.update_selection_box()
               ic(self.all_ships[self.selected_ship].ship_type)
               
            elif event.key == pg.K_RIGHT:
               self.selected_ship += 1 
               if self.selected_ship > len(self.all_ships) - 1:
                    self.selected_ship = 0
               self.update_selection_box()
               ic(self.all_ships[self.selected_ship].ship_type)
               

            elif event.key == pg.K_RETURN:
                return(self.handle_action())
        
            

    def draw(self, surface, overlay) -> None:
        surface.fill((0,0,0,0))
        
        self.selection_sprites.draw(surface)
        self.all_ship_sprites.draw(surface)
        
        for index, option in enumerate(self.options):
            text_render = self.render_text(index)
            surface.blit(text_render, self.get_text_position(text_render, index, surface))
