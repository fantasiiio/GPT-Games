import pygame
import os

class Animation:
    def __init__(self, screen, base_folder, prefix, action_name, is_looping, offset, offset_angle):
        self.offset_angle = offset_angle
        self.screen = screen
        self.images = []
        self.rects = []
        self.current_frame = 0
        self.frame_duration = 100  # in milliseconds, adjust as needed
        self.last_update = pygame.time.get_ticks()
        self.action_name = action_name
        self.is_looping = is_looping # -1 = always, 0 = never, > 0 = number of times
        self.loop_count = 0
        self.is_playing = False
        self.load_action(base_folder, prefix ,action_name)
        self.offset = offset

    def get_current_rect(self):
        return self.rects[self.current_frame]

    def rotate_image(self, image, angle, rotation_center=None):
        original_rect = image.get_rect()
        
        # Create an expanded surface to ensure the entire image remains visible after rotation
        expanded_size = int(max(image.get_width(), image.get_height()) * 1.414)  # 1.414 = sqrt(2) to handle diagonal size
        new_surface = pygame.Surface((expanded_size, expanded_size), pygame.SRCALPHA, 32)
        new_surface.blit(image, (expanded_size // 2 - image.get_width() // 2, 
                                expanded_size // 2 - image.get_height() // 2))
        
        rotated_image = pygame.transform.rotate(new_surface, angle)
        
        # Get the rectangle of the rotated image
        rotated_rect = rotated_image.get_rect()

        # If no rotation center is provided, use the image's center
        if rotation_center is None:
            rotation_center = original_rect.center

        # Adjust the position of the rotated image based on the specified rotation center
        rotated_rect.center = (rotation_center[0] + original_rect.width // 2 - expanded_size // 2, 
                            rotation_center[1] + original_rect.height // 2 - expanded_size // 2)

        return rotated_image, rotated_rect

    def blitRotate(self, surf, image, pos, originPos, angle):
        angle += self.offset_angle
        # offset from pivot to center
        image_rect = image.get_rect(topleft = (pos[0] - originPos[0], pos[1]-originPos[1]))
        offset_center_to_pivot = pygame.math.Vector2(pos) - image_rect.center
        
        # roatated offset from pivot to center
        rotated_offset = offset_center_to_pivot.rotate(-angle)

        # rotated image center
        rotated_image_center = (pos[0] - rotated_offset.x, pos[1] - rotated_offset.y)

        # Create an expanded surface to ensure the entire image remains visible after rotation
        expanded_size = int(max(image.get_width(), image.get_height()) * 1.414)  # 1.414 = sqrt(2) to handle diagonal size
        new_surface = pygame.Surface((expanded_size, expanded_size), pygame.SRCALPHA, 32)
        new_surface.blit(image, (expanded_size // 2 - image.get_width() // 2, 
                                expanded_size // 2 - image.get_height() // 2))


        # get a rotated image
        rotated_image = pygame.transform.rotate(new_surface, angle)
        rotated_image_rect = rotated_image.get_rect(center = rotated_image_center)

        rotated_image_rect.x += self.offset[0]
        rotated_image_rect.y += self.offset[1]
        # rotate and blit the image
        surf.blit(rotated_image, rotated_image_rect)
        return rotated_image, rotated_image_rect




    def draw(self, x, y, angle=0, rotation_center=None):
        image = self.images[self.current_frame]
        if rotation_center is None:
            rotation_center = image.get_rect().center
            
        return self.blitRotate(self.screen, image, (x,y), rotation_center, angle)        
    

    def get_outline(self, image,color=(0,0,0)):
        rect = image.get_rect()
        mask = pygame.mask.from_surface(image)
        outline = mask.outline(2)
        outline_image = pygame.Surface(rect.size).convert_alpha()
        outline_image.fill((0,0,0,0))
        for point in outline:
            outline_image.set_at(point,color)
        return outline_image

    def is_finished(self):        
        if self.is_looping == -1:
            return False
        if self.is_looping > 0 and self.loop_count >= self.is_looping:
            return True
            
        return self.current_frame == len(self.images) - 1

    def stop(self):
        self.is_playing = False

    def play(self):
        self.reset()
        self.is_playing = True
        self.current_frame = 0

    def load_action(self, base_folder, prefix, action):
        # count number of files in folder
        file_count = len([f for f in os.listdir(base_folder + f'\\{action}\\') if os.path.isfile(os.path.join(base_folder + f'\\{action}\\', f))])
        for i in range(1, file_count+1):
            formatted_number = str(i).zfill(2)
            file_name = base_folder + f'\\{action}\\{prefix}{action}_' + str(formatted_number) + '.png'
            # check if file exists
            if not os.path.isfile(file_name):
                continue
            img = pygame.image.load(file_name)
            img.convert_alpha()
            img.set_colorkey((0, 0, 0))
            self.rects.append(img.get_rect())
            self.images.append(img)

    def reset(self):
        self.loop_count = 0
        self.current_frame = 0
        self.last_update = pygame.time.get_ticks()

    def update(self, x, y):
        now = pygame.time.get_ticks()
        if self.is_playing and now - self.last_update > self.frame_duration:
            if self.is_looping > 0 and self.loop_count >= self.is_looping:
                return
            if self.current_frame == len(self.images) - 1 and self.is_looping == 0:
                return
            self.loop_count += 1
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % len(self.images)
