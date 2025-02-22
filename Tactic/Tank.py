from collections import deque
from Bullet import Bullet
from Animation import Animation
from Unit import Unit
import math
from config import *
import pygame
import random

class TankTower:
    def __init__(self, base_folder, screen, parent):
        self.parent = parent
        self.screen = screen
        self.animations = {}
        self.current_animation = "Idle"
        self.offset = (0,0)
        self.world_pos_x = 0
        self.world_pos_y = 0
        #self.parent_angle = 0
        self.angle = 0
        self.animations["Idle"] = Animation(self.screen,base_folder,"Tank_tower_", "Idle", 0, (0,0), 90)
        self.animations["Fire"] = Animation(self.screen,base_folder,"Tank_tower_", "Fire", 0, (0,0), 90)
        #self.animations["Shot"] = Animation(self.screen,base_folder,"Tank_tower_", "Shot", 0, (0,0), 90, 1400)
        self.animations["Broken"] = Animation(self.screen,base_folder,"Tank_tower_", "Broken", 0, (0,0), 90)
        #self.current_animation = "Fire"
        # self.animations["Fire"].play()
        #self.rotated_image_rect = self.animations[self.current_animation].get_current_rect()
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

        center = center[0], center[1] - 20
        if self.current_animation == "Fire":
            self.animations["Fire"].draw(self.draw_x, self.draw_y, -self.angle+180, (20,120), None, outline_color ,outline_thickness)
            self.animations["Idle"].draw(self.draw_x, self.draw_y, -self.angle, center, (0,0), outline_color ,outline_thickness)
        else:
            self.animations[self.current_animation].draw(self.draw_x, self.draw_y, -self.angle, center, (0,0), outline_color ,outline_thickness)
    
    def update(self, parent_pos, angle):

        rect =self.animations["Idle"].get_current_rect().copy()
        rect.center = (parent_pos[0] + self.parent.offset[0], parent_pos[1] + self.parent.offset[1])

        self.angle = angle

        rotated_corners  = self.parent.rotate_rect(rect, self.angle + 90)
        #pygame.draw.polygon(self.screen, (0, 0, 255), rotated_corners, 2)
        self.shoot_position = self.parent.get_shoot_positions(rotated_corners, 0, 10)
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



class Tank(Unit):
    def __init__(self, target_tile, player, grid,  base_folder=f"{base_path}\\assets\\images\\Tank", screen=None, gun_sound_file=f"{base_path}\\assets\\sounds\\tank shots.wav", action_finished=None, id=None):
        super().__init__(target_tile, player, grid, base_folder, screen,"Tank", action_finished, id = id)
        self.engine_sound = pygame.mixer.Sound(f"{base_path}\\assets\\sounds\\tankEngine.wav")
        self.bullet_explosion_sound = pygame.mixer.Sound(f"{base_path}\\assets\\sounds\\explosion 1.wav")
        self.explosion_sound = pygame.mixer.Sound(f"{base_path}\\assets\\sounds\\explosion 2.wav")
        self.gun_sound = pygame.mixer.Sound(gun_sound_file)

        self.actions = {"Move To", "Fire", "Get Out"}
        self.child = TankTower(base_folder, screen, self)
        self.screen = screen
        self.animations = {}
        self.current_animation = "Idle"
        self.current_action = None


        self.offset = (32,32)
        self.child.offset = tuple(a + b for a, b in zip(self.child.offset, self.offset))

        self.load_animations(base_folder)
        self.animations["Idle"].play()
        self.velocity_x = 0
        self.velocity_y = 0
        self.last_fired = pygame.time.get_ticks()  # Time when the last bullet was fired
        self.bullets_fired = 0  # Number of bullets fired
        self.canon_number = 0
        #self.driver = None
        self.passengers = []
        self.target_x = 0
        self.target_y = 0
        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.angle = 0
        self.is_vehicle = True


    def load_animations(self, base_folder):
        self.animations["Idle"] = Animation(self.screen,base_folder,"Tank_base_", "Idle", -1, self.offset, 90)
        self.bullet_image = Animation(self.screen,base_folder,"", "Bullet", -1, self.offset, 90) 
        self.bullet_explosion_animation = Animation(self.screen, f"{base_path}\\assets\\images\\Effects","", "Explosion", 0, self.offset, 0, frame_duration=25) 
        self.explosion_animation = Animation(self.screen, f"{base_path}\\assets\\images\\Effects","Explosion_", "1", 0, self.offset, 0, frame_duration=25) 
        #SpriteLayers.add_animation("top", self.explosion_animation) 
        #self.animations["Move"] = Animation(self.screen,base_folder,"Tank_base_", "Move", -1, self.offset, 90)
        self.animations["Broken"] = Animation(self.screen,base_folder,"Tank_base_", "Broken", 0, self.offset, 90)
    



