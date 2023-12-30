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
        self.explosion = False  # nothing starts out exploding

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

        # EnemyAI sprite group
        self.enemy_ai_sprites = pg.sprite.GroupSingle()
        self.enemy_ai_sprites.add(self.enemy)

        # Explosion sprite group
        self.explosion = pg.sprite.GroupSingle()
        self.explosion.add

        # Win and loss sounds
        self.sound_win = pg.mixer.Sound("assets/sounds/win_1.wav")
        self.sound_loss = pg.mixer.Sound("assets/sounds/lose_1.wav")

        self.sound_win.set_volume(0.5)
        self.sound_win.set_volume(0.5)

    def get_event(self, event) -> str | None:
        self.player.get_event(event)
        if self.state != "run":
            return self.state

    # Update all objects
    def update(self) -> None:
        if not self.explosion:
            self.player.update()

            # Updates the players's projectile sprites
            self.player.projectiles.update()
            self.player.engine_trails.update()

            # Update enemies and their projectiles
            self.enemy.update()

            self.enemy.projectiles.update()
            self.enemy.engine_trails.update()

            self.enemy.ai.update(self.player)
            # Update obstacles

            # Check collisions
            # Enemy collision
            gets_hit = pg.sprite.spritecollide(self.enemy, self.player.projectiles, True)
            for projectile_hit in gets_hit:
                projectile_hit.kill()

                self.state = "win"
                pg.mixer.stop()
                # TODO: fix zoom level

                self.explosion = True
                self.exploder = self.enemy
                self.start_time = pg.time.get_ticks()

                self.explosion_x = self.enemy.state.x_pos
                self.explosion_y = self.enemy.state.y_pos
                self.sound_win.play()

            # Player collision
            gets_hit = pg.sprite.spritecollide(self.player, self.enemy.projectiles, True)
            for projectile_hit in gets_hit:
                projectile_hit.kill()

                self.state = "loss"
                pg.mixer.stop()

                self.explosion = True
                self.exploder = self.player
                self.start_time = pg.time.get_ticks()
                self.explosion_x = self.player.state.x_pos
                self.explosion_y = self.player.state.y_pos
                self.sound_loss.play()

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
        self.player.engine_trails.draw(surface)

        self.enemy_ai_sprites.draw(surface)
        self.enemy.projectiles.draw(surface)
        self.enemy.engine_trails.draw(surface)

        if self.explosion == True:
            x = self.explosion_x + random.randint(-30, 30)
            y = self.explosion_y + random.randint(-30, 30)
            radius = random.randint(5, 25)
            red_green = random.randint(128, 255)
            color = pg.Color(red_green, 255 - red_green, 0, random.randint(0, 255))

            pg.draw.circle(surface, color, (x, y), radius=radius, width=radius)
            if pg.time.get_ticks() - self.start_time > 1000:  # first disappear ship
                self.exploder.kill()
            elif pg.time.get_ticks() - self.start_time > 1500:  # then stop exploding
                ic("stop exploding!")
                self.explosion = False
