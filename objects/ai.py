import math
from icecream import ic

class AI:
    def __init__(self, ai, skill, ship_type, config) -> None:
        self.skill = skill
        self.ai = ai
        self.ship_type = ship_type
        self.config = config

        # Behavior
        # attack: attacks player
        # flee: tries to get away from player because of low health or energy
        # (if low health -> tries to get to timeout alive, low energy -> recharge and switch to attack)

        # Attitudes
        # ranged: attacks from a distance
        # close: tries to get close to player
        # aggressive: given the opportunity, will attack if diff in attack angle and heading is < 15
        # recharging: trying to preserve energy

        self.behavior = ['attack']  # we start attacking
        self.attitude = ['close', 'aggressive']  # we charge towards player

    def update(self, player, obstacles) -> None:
        """
        Basic enemy AI, simulating inputs

        """
        self.ai.rect.centerx = self.ai.x_pos
        self.ai.rect.centery = self.ai.y_pos

        distance = ((self.ai.x_pos - player.x_pos)**2 + (self.ai.y_pos - player.y_pos)**2)**0.5

        
        # Identify the line between the AI and the player
        # Remember: 0 degrees is up, angle increases counter-clockwise
        target_line = (self.ai.x_pos, self.ai.y_pos), (player.x_pos, player.y_pos)
        target_angle_rad = math.atan2(player.y_pos - self.ai.y_pos, player.x_pos - self.ai.x_pos) + math.pi/2
        target_angle = 360-math.degrees((target_angle_rad + 2 * math.pi) % (2 * math.pi))  # angle from AI to player

        # We now know the attack angle, but we must consider obstacles and attitude
        #print(f'vector angle: {target_angle:.2f}, heading ai: {self.ai.heading:.1f}, heading player: {player.heading:.1f}')

        # find which direction turn in the shortest - clockwise (decreasing angle) or counter-clockwise (increasing angle)
        attack_angle = target_angle - self.ai.heading + 360 if target_angle - self.ai.heading < 0 else target_angle - self.ai.heading
        flight_angle = attack_angle - 180 + 360 if attack_angle - 180 < 0 else attack_angle - 180
        self.ai.turning = 0
        self.turning_target = 0
        self.ai.firing = 0
        self.ai.slow_turn = False  # if True, the ship turns at half the turn rate

        '''
        Attack behavior pattern
        '''
        if 'attack' in self.behavior:
            # AI turns towards player
            if attack_angle > self.ai.ship_config['turn_speed'] and attack_angle < 360 - self.ai.ship_config['turn_speed']:
                self.ai.turning = -1 if attack_angle > 180 else 1  # turn to target

            # If distance is high, we fire only with almost full energy and high confidence
            if distance > self.config.window_size_xy * 0.7 and self.ai.energy > self.ai.ship_config['max_energy'] * 0.8 and 'confident' in self.attitude:
                self.ai.firing = True

            # If distance is low, we fire only even with almost no energy
            if distance <= self.config.window_size_xy * 0.7 and self.ai.energy > self.ai.ship_config['max_energy'] * 0.1:
                self.ai.firing = True

            # If we have an obstacle between us, stop firing, try avoiding
            for obstacle in obstacles:
                if obstacle.rect.clipline(target_line):
                    #print(f'OBSCURED, target angle {math.degrees(target_angle)}')
                    self.ai.firing = False
                    self.ai.turning = 1
                    self.ai.slow_turn = True

            # We try to close the distance in 'hunt' mode
            if distance > self.config.window_size_xy * 0.1:
                self.ai.accelleration = 1

        '''
        Flee behavior pattern
        '''    
        # AI turns away from player and accelerates
        if attack_angle > self.ai.ship_config['turn_speed'] and attack_angle < 360 - self.ai.ship_config['turn_speed']:
                self.ai.turning = -1 if attack_angle > 180 else 1  # turn to target
                self.ai.accelleration = 1


        '''
        Behavior independent attitude controlled actions
        '''
        # AI wants to fire
        if self.ai.firing:
            if 'aggressive' in self.attitude and abs(target_angle - self.ai.heading) > 5:  # fire liberally
                self.ai.firing = False
            if 'recharging' in self.attitude and abs(target_angle - self.ai.heading) > 3:  # fire only when sure
                self.ai.firing = False

        # Overrides
        if self.ai.under_gravity:
            ic('PANINC')

        # # Adjust attitudes
        # if self.ai.energy < self.ai.max_energy * 0.1:  # less than 10% energy
        #     self.attitude.remove('aggressive')
        #     self.attitude.append('flee')
        # else: 
        #     pass



