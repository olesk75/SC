from objects.players import Player, EnemyAI

import pygame as pg
from icecream import ic


class Level:
    def __init__(self) -> None:
        self.number: int
        self.enemyAI_difficulty = 1

        self.projectiles_live = 0

        self.player = Player(
            x_pos=100,
            y_pos=100,
            health=1000,
            shield=1000,
            direction=90,
            velocity=0,
            heading=10,
            max_velocity=100,
        )
        self.enemy = EnemyAI(
            x_pos=100,
            y_pos=100,
            health=1000,
            shield=1000,
            direction=90,
            velocity=0,
            heading=10,
            skill=self.enemyAI_difficulty,
            max_velocity=100,
        )

    # Set up all sprite groups
    def startup(self, number) -> None:
        ic("Instancing new level", number)
        self.number = number

        # Player sprite group
        self.player_sprites = pg.sprite.GroupSingle()
        self.player_sprites.add(self.player)

        # Projectile sprite goup
        self.projectile_sprites = pg.sprite.Group()

        # EnemyAI sprite group
        self.enemy_ai_sprites = pg.sprite.GroupSingle()

    def get_event(self, event) -> None:
        self.player.get_event(event)

    # Update all object
    def update(self) -> None:
        self.player.update()

        # Updates the players's projectile sprites
        self.player.projectiles.update()

        ic(len(self.player.projectiles.sprites()))
        # Update enimies and their projectiles

        # Update obstacles

    # Draw all sprite groups + background
    def draw(self, surface) -> None:
        # placeholder background
        surface.fill(pg.Color("#AAAAAA"))

        self.player_sprites.draw(surface)
        self.player.projectiles.draw(surface)

        # Placeholder
        self.enemy_ai_sprites.draw(surface)
