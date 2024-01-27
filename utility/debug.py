import pygame as pg


def debug(info, x=20, y=20, surface=None, color='White') -> None:
    """
    Provides debug information on the screen surface during play for debugging

    Often part of the draw() funtion at the lvl level where it can access the relevant data
    """
    font = pg.font.Font("freesansbold.ttf", 32)
    if not surface:
        surface = pg.display.get_surface()

    debug_surface = font.render(str(info), True, color)
    debug_rect = debug_surface.get_rect(topleft=(x, y))
    
    pg.draw.rect(surface, 'Black', debug_rect)
    surface.blit(debug_surface, debug_rect)
