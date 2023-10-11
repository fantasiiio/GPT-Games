from collections import deque
from Bullet import Bullet
from Animation import Animation
from Unit import Unit
import math
from config import *
import pygame
import random
import time

class HelicopterBlades():
    def __init__(self, base_folder, screen, parent):
        self.parent = parent
        self.screen = screen
        self.animations = {}
        self.current_animation = "Idle"
        self.offset = (0,0)
        #self.parent_angle = 0
        self.angle = 0
        self.world_pos_x = 0
        self.world_pos_y = 0        
        self.animations["Idle"] = Animation(self.screen,base_folder,"Helicopter_blades_", "Idle", 0, (0,-10),90)
        self.animations["Slow"] = Animation(self.screen,base_folder,"blades_", "Move_slow", -1, (0,-10),90, frame_duration=50)
        self.animations["Fast"] = Animation(self.screen,base_folder,"blades_", "Move_fast", -1, (0,-10),90, frame_duration=50)
        self.animations["Slow"].play()
        self.animations["Fast"].play()
        self.draw_x = 0
        self.draw_y = 0

    def draw(self):
        center = self.animations["Idle"].get_current_rect().center

        outline_color=None
        outline_thickness=None
        if self.parent.swapped:
            if self.parent.player == self.parent.current_player:
                outline_color = (0, 255, 0)
            else:
                outline_color = (255, 0, 0)
            outline_thickness = 5
        elif self.parent.player != self.parent.current_player:
            if self.parent.player != 1:
                outline_color = (255, 0, 0)
                outline_thickness = 2
        elif self.parent.is_planning:
            outline_color = (0, 255, 0)
            outline_thickness = 4
            outline_fade = True

        center = center[0], center[1] - 10
        if self.current_animation == "Fire":
            self.animations["Shot"].draw(self.draw_x, self.draw_y, -self.angle, (46, 32), outline_color ,outline_thickness)
            self.animations["Fire"].draw(self.draw_x, self.draw_y, -self.angle, (46,-10), outline_color ,outline_thickness)
        else:
            self.animations[self.current_animation].draw(self.draw_x, self.draw_y, -self.angle, center, (0,0), outline_color ,outline_thickness, scale=self.parent.scale_factor)


    def update(self, parent_pos, angle):

        rect =self.animations["Idle"].get_current_rect().copy()
        rect.center = (parent_pos[0] + self.parent.offset[0], parent_pos[1] + self.parent.offset[1])

        self.angle = angle

        rotated_corners  = self.rotate_rect(rect, self.angle + 90)
        #pygame.draw.polygon(self.screen, (0, 0, 255), rotated_corners, 2)
        self.shoot_position = self.get_shoot_positions(rotated_corners, 0, 10)
        # pygame.draw.circle(self.screen, (0,0,0), self.shoot_position, 2)
        # pygame.draw.circle(self.screen, (0,0,0), self.shoot_positions[1], 2)
        self.world_pos_x = parent_pos[0] + self.offset[0]
        self.world_pos_y = parent_pos[1] + self.offset[1]
        self.draw_x = self.world_pos_x + self.parent.grid.get_camera_screen_position()[0]
        self.draw_y = self.world_pos_y + self.parent.grid.get_camera_screen_position()[1] 

        for animation in self.animations.values():
            animation.update() 

        # if self.current_animation == "Fire":
        #     finished = self.animations["Fire"].is_finished() and self.animations["Shot"].is_finished()
        #     if finished:
        #         self.animations["Shot"].reset()
        #         self.animations["Fire"].reset()
        #         self.current_animation = "Idle"



class Helicopter(Unit):
    def __init__(self, target_tile, player, grid, base_folder=f"{base_path}\\assets\\images\\Helicopter", screen=None, gun_sound_file=f"{base_path}\\assets\\sounds\\helicoptergun.wav", action_finished=None, id=None):
        super().__init__(target_tile, player, grid, base_folder, screen, "Helicopter", action_finished, id = id)
        self.engine_sound = pygame.mixer.Sound(f"{base_path}\\assets\\sounds\\helicopterEngine.wav")
        self.take_off_sound = pygame.mixer.Sound(f"{base_path}\\assets\\sounds\\helicopterTakeOff.wav")
        self.landing_sound = pygame.mixer.Sound(f"{base_path}\\assets\\sounds\\helicopterLanding.wav")

        self.actions_ground = {"Get Out", "Take Off"}
        self.actions_altitude = {"Move To", "Fire", "Landing"}
        self.actions = self.actions_ground
        self.child = HelicopterBlades(base_folder, screen, self)
        self.screen = screen
        self.animations = {}
        self.current_animation = "Idle"
        self.offset = (32,32)
        self.child.offset = tuple(a + b for a, b in zip(self.child.offset, self.offset))
        self.load_animations(base_folder)
        self.animations["Idle"].play()
        self.angle = 0
        self.velocity_x = 0
        self.velocity_y = 0
        self.last_fired = pygame.time.get_ticks()  # Time when the last bullet was fired
        self.bullets_fired = 0  # Number of bullets fired
        self.target_tile = target_tile
        self.canon_number = 0
        #self.driver = None
        self.passengers = []
        self.target_x = 0
        self.target_y = 0
        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.angle = 90
        self.child.angle = self.angle
        self.altitude_scale_factor = 1.5  # Target size is 1.5 times the original size
        self.time_to_reach_altitude = 1.0  # Time in seconds to reach the target size
        rect = self.animations["Idle"].get_current_rect()
        self.original_width, self.original_height = rect.width, rect.height
        self.scale_factor = 1.0
        self.going_up = 1
        self.last_action_time = None
        self.take_off_sound_channel = None
        self.take_off_sound_playing = None
        self.landing_sound_channel = None
        self.landing_sound_playing = None
        self.is_vehicle = True

        # Calculate the scaling factor per frame
        self.altitude_delta_width = (self.altitude_scale_factor - 1) * self.original_width / (self.time_to_reach_altitude * 60)

        # self.child.animations["Fire"].play() 
    
    def take_damage(self, damage):
        pass

    def load_animations(self, base_folder):
        self.animations["Idle"] = Animation(self.screen,base_folder,"Helicopter_base_", "Idle", 0, self.offset, 90)
        self.bullet_image = Animation(self.screen,base_folder,"", "Bullet", -1, self.offset, 90) 
        self.bullet_explosion_animation = Animation(self.screen, f"{base_path}\\assets\\images\\Effects","", "Explosion", 0, self.offset, 0, frame_duration=25) 
        self.explosion_animation = Animation(self.screen, f"{base_path}\\assets\\images\\Effects","Explosion_", "1", 0, self.offset, 0, frame_duration=25) 
        #self.animations["Broken"] = Animation(self.screen,base_folder,"Helicopter_base_", "Broken", 0, self.offset, 90)

    def take_off(self):
        self.going_up = 0
        self.current_action = "Taking Off"
        self.actions = self.actions_altitude
        self.take_off_sound_channel = self.take_off_sound.play()
        self.take_off_sound_playing = True
        self.child.current_animation = "Slow"       

    def land(self):
        self.going_up = -1
        self.current_action = "Landing"
        self.actions = self.actions_ground
        self.engine_sound.play(-1)


    def start_helicopter(self):
        if self.take_off_sound_playing and not self.take_off_sound_channel.get_busy():
            self.take_off_sound_playing = False
            self.engine_sound.play(-1)
            self.child.current_animation = "Fast"
            self.going_up = 1

        if self.going_up == 1:
            if self.scale_factor < self.altitude_scale_factor:
                self.scale_factor += self.altitude_delta_width / self.original_width  # Update scale factor
            else:
                self.scale_factor = self.altitude_scale_factor
                self.going_up = 0
                self.current_action = None
                self.engine_sound.stop()             


    def shut_down_helicopter(self):
        if self.landing_sound_playing and not self.landing_sound_channel.get_busy():
            self.landing_sound_playing = False
            self.child.current_animation = "Idle"
            self.going_up = 0
            self.current_action = None

        if self.going_up == -1:
            if self.scale_factor > 1:
                self.scale_factor -= self.altitude_delta_width / self.original_width
            else:
                self.scale_factor = 1
                self.going_up = 0                
                self.engine_sound.stop()
                self.landing_sound_channel = self.landing_sound.play()
                self.landing_sound_playing = True
                self.child.current_animation = "Slow"       

