import time
import math
import random
import pygame as pg
from icecream import ic
from settings import SCREEN_HEIGHT, SCREEN_WIDTH

class AI:
    def __init__(self, ai, skill, ship_type) -> None:
        self.skill = skill
        self.ai = ai
        self.ship_type = ship_type
        self.state_change_triggered = False
        self.trigger_time: float

        self.state = "calculating"  # ai starts hunting
        self.attitude = ['hunt', 'aggressive', 'confident']  # used to make decisions

    def _change_state(self, new_state) -> None:
        # We flip the switch if this is the first request to change state
        if not self.state_change_triggered:
            self.state_change_triggered = True
            self.trigger_time = time.time()
            self.old_state = self.state
        elif time.time() - self.trigger_time > 1 - self.skill:
            self.state = new_state

    def update(self, player, obstacles) -> None:
        """
        Basic enemy AI, simulating inputs

        """
        self.ai.rect.centerx = self.ai.x_pos
        self.ai.rect.centery = self.ai.y_pos

        distance = ((self.ai.x_pos - player.x_pos)**2 + (self.ai.y_pos - player.y_pos)**2)**0.5

        if self.state == "calculating":
            # Identify the line between the AI and the player
            # Remember: 0 degrees is up, angle increases counter-clockwise
            target_line = (self.ai.x_pos, self.ai.y_pos), (player.x_pos, player.y_pos)
            target_angle_rad = math.atan2(player.y_pos - self.ai.y_pos, player.x_pos - self.ai.x_pos) + math.pi/2
            target_angle = 360-math.degrees((target_angle_rad + 2 * math.pi) % (2 * math.pi))  # angle from AI to player

            

            # We now know the attack angle, but we must consider obstacles and attitude
            #print(f'vector angle: {target_angle:.2f}, heading ai: {self.ai.heading:.1f}, heading player: {player.heading:.1f}')

            # 1) find which direction turn in the shortest - clockwise (decreasing angle) or counter-clockwise (increasing angle)
            attack_angle = target_angle - self.ai.heading 
            attack_angle = attack_angle + 360 if attack_angle < 0 else attack_angle
            flight_angle = attack_angle - 180
            flight_angle = flight_angle + 360 if flight_angle < 0 else flight_angle

            self.ai.turning = 0
            self.turning_target = 0
            self.ai.firing = 0
            

            # AI is chasing player
            if 'hunt' in self.attitude:
                # AI turns towards player
                if attack_angle > self.ai.turn_speed and attack_angle < 360 - self.ai.turn_speed:
                    self.ai.turning = -1 if attack_angle > 180 else 1  # turn to target

                # If distance is high, we fire only with almost full energy and high confidence
                if distance > SCREEN_WIDTH * 0.7 and self.ai.energy > self.ai.max_energy * 0.8 and 'confident' in self.attitude:
                    print('FAR and FULL ENERGY')
                    self.ai.firing = True

                # If distance is low, we fire only even with almost no energy
                if distance <= SCREEN_WIDTH * 0.7 and self.ai.energy > self.ai.max_energy * 0.1:
                    print('CLOSE ATTACK IGNORING ENERGY')
                    self.ai.firing = True

                # If we have an obstacle between us, stop firing, try avoiding
                for obstacle in obstacles:
                    if obstacle.rect.clipline(target_line):
                        print(f'OBSCURED, target angle {math.degrees(target_angle)}')
                        self.ai.firing = False
                        #if not self.ai.turning:  #  if we're not already turning, turn random direction
                            #self.ai.turning = random.choice([1, -1])
                        self.ai.turning = 1

                # We try to close the distance in 'hunt' mode
                if distance > SCREEN_WIDTH * 0.1:
                    self.ai.accelleration = 1

            # Adjust attitudes
            # if self.ai.energy < self.ai.max_energy * 0.1:  # less than 10% energy
            #     self.attitude.remove('hunt')
            #     self.attitude.append('flee')
            # else: 



