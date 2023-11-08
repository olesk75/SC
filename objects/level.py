from objects.players import Player, EnemyAI
from objects.background import Background
from settings import SCREEN_HEIGHT, SCREEN_WIDTH

import pygame as pg
from icecream import ic
import random


class Level:
    def __init__(self) -> None:
        self.number: int
        self.state = "run"  # alternatives "win" and "loss"
        self.enemyAI_difficulty = 0.5  # float between 0 and 1
        self.zoom = 1  # we zoom out when opponents get far appart

        self.projectiles_live = 0

    # Set up players and all sprite groups
    def startup(self, number) -> None:
        self.background = Background()

        self.player = Player(
            x_pos=random.randint(100, SCREEN_WIDTH - 100),
            y_pos=random.randint(100, SCREEN_HEIGHT - 100),
            heading=random.random() * 359,
            ship_type="martian",
        )

        self.enemy = EnemyAI(
            x_pos=random.randint(100, SCREEN_WIDTH - 100),
            y_pos=random.randint(100, SCREEN_HEIGHT - 100),
            heading=random.random() * 359,
            ship_type="plutonian",
            skill=self.enemyAI_difficulty,
        )

        ic("Instancing new level", number)
        self.number = number

        # Player sprite group
        self.player_sprites = pg.sprite.GroupSingle()
        self.player_sprites.add(self.player)

        # Projectiles sprite goup
        self.projectile_sprites = pg.sprite.Group()

        # EnemyAI sprite group
        self.enemy_ai_sprites = pg.sprite.GroupSingle()
        self.enemy_ai_sprites.add(self.enemy)

    def get_event(self, event) -> str | None:
        self.player.get_event(event)
        if self.state != "run":
            return self.state

    # Update all objects
    def update(self) -> None:
        # self.enemy.think(self.player, self.player.projectiles)
        self.player.update()

        # Updates the players's projectile sprites
        self.player.projectiles.update()

        # Update enimies and their projectiles
        self.enemy.update()

        self.enemy.projectiles.update()

        self.enemy.think(self.player, self.player.projectiles)
        # Update obstacles

        # Check collisions
        # Enemy collision
        gets_hit = pg.sprite.spritecollide(self.enemy, self.player.projectiles, True)
        for projectile_hit in gets_hit:
            projectile_hit.kill()
            self.enemy.kill()
            self.state = "win"

        # Player collision
        gets_hit = pg.sprite.spritecollide(self.player, self.enemy.projectiles, True)
        for projectile_hit in gets_hit:
            projectile_hit.kill()
            self.player.kill()
            self.state = "loss"

    # Draw all sprite groups + background
    def draw(self, surface) -> None:
        self.background.draw(
            surface,
            "Player 1",
            self.player.state.health,
            self.player.state.energy,
            "Enemy AI",
            self.enemy.state.health,
            self.enemy.state.energy,
        )

        self.player_sprites.draw(surface)
        self.player.projectiles.draw(surface)
        self.enemy_ai_sprites.draw(surface)
        self.enemy.projectiles.draw(surface)
