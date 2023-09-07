import pygame
import os

class Animation:
    def __init__(self, screen, base_folder, action_name, is_looping):
        self.screen = screen
        self.images = []
        self.current_frame = 0
        self.frame_duration = 100  # in milliseconds, adjust as needed
        self.last_update = pygame.time.get_ticks()
        self.action_name = action_name
        self.is_looping = is_looping
        self.is_playing = True
        self.load_action(base_folder, action_name)

    def rotate_image_without_black_border(self,image, angle_degrees):
        # Create a new transparent surface larger than the original image
        expanded_size = max(image.get_width(), image.get_height())
        new_surface = pygame.Surface((expanded_size, expanded_size), pygame.SRCALPHA, 32)
        
        # Blit the image to the center of the new surface
        new_surface.blit(image, (expanded_size // 2 - image.get_width() // 2, 
                                expanded_size // 2 - image.get_height() // 2))
        
        # Rotate the new surface
        rotated_image = pygame.transform.rotate(new_surface, -angle_degrees)
        
        return rotated_image


    def draw(self, x, y, angle=0):
        image = self.images[self.current_frame]
        rotated_image = self.rotate_image_without_black_border(image, -angle)
        self.screen.blit(rotated_image, (x, y))        
        #self.screen.blit(self.images[self.current_frame], (x, y))

    def is_finished(self):
        return self.current_frame == len(self.images) - 1

    def stop(self):
        self.is_playing = False

    def play(self):
        self.is_playing = True
        self.current_frame = 0

    def load_action(self, base_folder, action):
        # count number of files in folder
        file_count = len([f for f in os.listdir(base_folder + f'\\{action}\\') if os.path.isfile(os.path.join(base_folder + f'\\{action}\\', f))])
        for i in range(1, file_count+1):
            formatted_number = str(i).zfill(2)
            img = pygame.image.load(base_folder + f'\\{action}\\Gunner{action}_' + str(formatted_number) + '.png')
            img.convert_alpha()
            img.set_colorkey((0, 0, 0))
            self.images.append(img)

    def reset(self):
        self.current_frame = 0
        self.last_update = pygame.time.get_ticks()

    def update(self, x, y):
        now = pygame.time.get_ticks()
        if self.is_playing and now - self.last_update > self.frame_duration:
            if self.current_frame == len(self.images) - 1 and not self.is_looping:
                return
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % len(self.images)
