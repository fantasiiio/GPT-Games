import pygame
import os
import time
import math
class Animation:
    start_time = time.time() 
    def __init__(self, screen, base_folder, prefix, action_name, is_looping, offset, offset_angle, total_loop_time=None, frame_duration = 100, outline_image=None):
        self.offset_angle = offset_angle
        self.screen = screen
        self.images = []
        self.rects = []
        self.current_frame = 0
        self.frame_duration = frame_duration  # in milliseconds, adjust as needed
        self.last_update = pygame.time.get_ticks()
        self.action_name = action_name
        self.is_looping = is_looping # -1 = always, 0 = never, > 0 = number of times
        self.loop_count = 0
        self.is_playing = False
        self.load_action(base_folder, prefix ,action_name)
        self.offset = offset
        self.frames_count = 0
        self.outline_image = None
        self.rotated_image_cache = {}
        
        if outline_image:
            self.load_outline_image(outline_image)

        if total_loop_time:
            self.frames_required = total_loop_time // self.frame_duration
        else:
            self.frames_required = None

        
        self.time_played = 0  # Initialize the time_played to zero

    def load_outline_image(self, outline_image_file):
        self.outline_image = pygame.image.load(outline_image_file)
        self.outline_image.convert_alpha()

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

    def blitRotate(self, image, pos, originPos, angle, offset=None):
        offset = self.offset if offset is None else offset
        angle += self.offset_angle

        # Compute this once and cache the results if the image size doesn't change.
        max_dim = max(image.get_width(), image.get_height())
        expanded_size = int(max_dim * 1.414)  # sqrt(2)

        # Cache the rotated image and use that if angle doesn't change.
        # rotated_image = your_cached_rotated_image

        image_rect = image.get_rect(topleft=(pos[0] - originPos[0], pos[1] - originPos[1]))
        offset_center_to_pivot = pygame.math.Vector2(pos) - image_rect.center

        # Reuse if you can
        rotated_offset = offset_center_to_pivot.rotate(-angle)
        rotated_image_center = (pos[0] - rotated_offset.x, pos[1] - rotated_offset.y)

        # Check if we've already cached a rotated image for this angle
        if angle not in self.rotated_image_cache:
            new_surface = pygame.Surface((expanded_size, expanded_size), pygame.SRCALPHA, 32)
            new_surface.blit(image, (expanded_size // 2 - image.get_width() // 2,
                                    expanded_size // 2 - image.get_height() // 2))
            rotated_image = pygame.transform.rotate(new_surface, angle)
            self.rotated_image_cache[angle] = rotated_image  # Cache it for later
        else:
            rotated_image = self.rotated_image_cache[angle]

        rotated_image_rect = rotated_image.get_rect(center=rotated_image_center)
        rotated_image_rect.x += offset[0]
        rotated_image_rect.y += offset[1]

        return rotated_image, rotated_image_rect



    def draw(self, x, y, angle=0, rotation_center=None, offset=None, outline_color=None, outline_thickness=None, outline_fade = False, scale = 1.0):
        image = self.images[self.current_frame]
        if rotation_center is None:
            rotation_center = image.get_rect().center
            
        rotated_image, rotated_image_rect = self.blitRotate(image, (x,y), rotation_center, angle, offset)
        if scale != 1.0:
            rotated_image = pygame.transform.scale(rotated_image, (int(rotated_image.get_width() * scale), int(rotated_image.get_height() * scale)))
            rotated_image_rect = rotated_image.get_rect(center = rotated_image_rect.center)

        self.screen.blit(rotated_image, rotated_image_rect)

        if outline_color and outline_thickness:  
            # Use the provided outline_image or default to the main image if not provided      
            outline_source = self.outline_image if self.outline_image else rotated_image
            outlined = self.draw_outline(outline_source, outline_color, outline_thickness, offset, outline_fade)
            outline_rect = outlined.get_rect(center = rotated_image_rect.center)
            self.screen.blit(outlined, outline_rect)

    def draw_outline(self, image, outline_color, outline_thickness, offset=None, fade = False):
        offset = self.offset if offset is None else offset        
        if fade:
            current_time = time.time()
            elapsed_time = current_time - self.start_time
            fade_factor = math.sin(elapsed_time*5)

            alpha_value = int((fade_factor + 1) / 2 * 255)
            outline_color = (*outline_color[:3], alpha_value)
        else:
            outline_color = (*outline_color[:3], 255)

        mask = pygame.mask.from_surface(image)
        outline_points = mask.outline()
        outlined_surface = pygame.Surface((image.get_width() + 2 * outline_thickness,
                                            image.get_height() + 2 * outline_thickness),
                                        pygame.SRCALPHA)
        for point in outline_points:
            pygame.draw.circle(outlined_surface, outline_color, (point[0] + outline_thickness, point[1] + outline_thickness), outline_thickness)

        return outlined_surface

    def is_finished(self):        
        if self.is_looping == -1:
            #print("Looping indefinitely.")
            return False
        
        if self.is_looping > 0 and self.loop_count >= self.is_looping:
            #print("Finished based on loop count.")
            return True

        if self.current_frame and self.frames_required and self.current_frame >= self.frames_required:
            #print(f"Finished based on current_frame. Current Frame: {self.current_frame}, Frames Required: {self.frames_required}")
            return True
        
        if self.current_frame == len(self.images) - 1:
            #print("Finished animation sequence.")
            return True

        #print("Animation not finished yet.")
        return False          

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
            # img.set_colorkey((0, 0, 0))
            self.rects.append(img.get_rect())
            self.images.append(img)
        if not self.images:
            raise ValueError(f"No images loaded for {base_folder}, {prefix}, {action}")
            return

    def reset(self):
        self.loop_count = 0
        self.current_frame = 0
        self.time_played = 0
        self.last_update = pygame.time.get_ticks()
        self.frames_count = 0

    def update(self):
        now = pygame.time.get_ticks()
        if self.is_playing and now - self.last_update > self.frame_duration:
            if self.is_looping > 0 and self.loop_count >= self.is_looping:
                #print("Stopped based on loop count.")
                self.stop()
                return
            
            if self.frames_required and self.frames_count >= self.frames_required:
                #print(f"Stopped based on frames_required. {self.frames_count}/{self.frames_required}")
                self.stop()
                return
            
            if not self.frames_required and self.frames_count == len(self.images) - 1 and self.is_looping == 0:
                #print("Stopped based on animation sequence.")
                self.stop()
                return
            
            self.time_played += now - self.last_update
            self.loop_count += 1
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % len(self.images)
            self.frames_count += 1