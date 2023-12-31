import time
import math
from icecream import ic
import random


class AI:
    def __init__(self, ai, skill, ship_type) -> None:
        self.skill = skill
        self.ai = ai
        self.ship_type = ship_type
        self.state_change_triggered = False
        self.trigger_time: float

        self.state = "hunting"  # ai starts hunting

    def _change_state(self, new_state) -> None:
        # We flip the switch if this is the first request to change state
        if not self.state_change_triggered:
            self.state_change_triggered = True
            self.trigger_time = time.time()
            self.old_state = self.state
        elif time.time() - self.trigger_time > 1 - self.skill:
            self.state = new_state

    def update(self, player) -> None:
        """
        Basic enemy AI, simulating inputs

        General rules:
         - starts *hunting (half speed, search pattern)
         - when player is found, starts *attacking (full speed, turn towards player)
         - if we are unable to get pointed at player (we are being outmanouvered),
           slow down until we're able to get the player in our crosshair
              - if we have teleport, use that as well
        - if we have player within ±10° of heading, we open fire
            - if energy < 25%, only fire if player within ±3° of heading
        - if we have shields, use them if the player gets a projectile close to us

        """
        # If we're either hunting or escaping, we accellerate to max
        # if set(['hunt', 'escape']).issubset(self.strategies):
        if self.state == "hunting":
            # Accelerate to half speed
            half_speed = self.ai.state.max_velocity / 2
            if self.ai.state.velocity < half_speed - 1:
                self.ai.accelleration = 1

            elif self.ai.state.velocity > half_speed + 1:
                self.ai.accelleration = -1
            else:
                self.ai.accelleration = 0

            if self.ai.turning == 0:
                self.ai.turning = random.choice([-1, 1])  # random turn direction

            # Determine potential state change
            # Calculate the vector to Player
            dx = player.rect.centerx - self.ai.rect.centerx
            dy = player.rect.centery - self.ai.rect.centery

            if dx + dy < 300:
                self._change_state("attacking")

        # TODO: define distance limits

        if self.state == "attacking":
            # Full speed ahead!
            if self.ai.state.velocity < self.ai.state.max_velocity:
                self.ai.accelleration = 1
            else:
                self.ai.accelleration = 0

            # Turn AI towards player
            # Calculate the vector to Player
            dx = player.rect.centerx - self.ai.rect.centerx
            dy = player.rect.centery - self.ai.rect.centery

            # Calculate the angle in degrees
            angle = math.atan2(-dx, -dy)
            angle %= 2 * math.pi
            angle = math.degrees(angle)

            # Perfect following: self.state.heading = angle
            angle_delta = angle - self.ai.state.heading
            if angle_delta < 0:
                angle_delta += 360

            self.ai.turning = 0

            if angle_delta > self.ai.turn_speed:
                if angle_delta >= 180:
                    self.ai.turning = -1
                elif angle_delta > 0:
                    self.ai.turning = 1

            else:
                # We got the player in our sights and we attack with main weapon
                self.ai.fire()

            if angle_delta > 90:  # AI lost sight of player
                self.state = "hunting"
