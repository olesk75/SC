import time
import math
from icecream import ic


class AI:
    def __init__(self, ai, skill, ship_type) -> None:
        self.skill = skill
        self.ai = ai
        self.ship_type = ship_type
        self.state_change_triggered = False
        self.trigger_time: float

        self.strategies = {"start"}

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
         - always turn towards the player
         - accellerate to max speed
         - if we are unable to get pointed at player (we are being outmanouvered),
           slow down until we're able to get the player in our crosshair
              - if we have teleport, use that as well
         - if we have shields, use them if the player gets a projectile close to us

        """

        ic(self.strategies)

        # We immediately go to hunt mode after start PLACEHOLDER
        if "start" in self.strategies:
            self.strategies = {"hunt"}

        # If we're either hunting or escaping, we accellerate to max
        # if set(['hunt', 'escape']).issubset(self.strategies):
        if "hunt" in self.strategies or "escape" in self.strategies:
            # Accelerate to max speed
            if self.ai.state.velocity < self.ai.state.max_velocity:
                self.ai.accelleration += 1
            else:
                self.ai.accelleration = 0

        if "hunt" in self.strategies:
            # Turn AI towards player

            # Calculate the vector to Player
            dx = player.rect.centerx - self.ai.rect.centerx
            dy = player.rect.centery - self.ai.rect.centery

            # Calculate the angle in radians
            angle = math.atan2(-dx, -dy)
            angle %= 2 * math.pi
            angle = math.degrees(angle)

            # Perfect following: self.state.heading = angle
            angle_delta = angle - self.ai.state.heading
            if angle_delta < 0:
                angle_delta += 360

            self.turning = 0

            if angle_delta > self.ai.turn_speed:
                if angle_delta >= 180:
                    self.ai.turning = -1
                elif angle_delta > 0:
                    self.ai.turning = 1

            else:
                # We got the player in our sights and we attack with main weapon
                self.strategies.add("fire")

        if "fire" in self.strategies:
            self.ai.fire()
