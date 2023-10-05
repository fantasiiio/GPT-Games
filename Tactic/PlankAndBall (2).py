import pygame
from pygame.locals import *
from Box2D import *
from Box2D.b2 import *
from math import sin, cos
import random
import math
import time

class PlankAndBall:
    def __init__(self, init_pygame=True, full_screen=False, screen=None):
        self.window_width = 0
        self.window_height = 0
        self.render_surface = None
        self.init_graphics(init_pygame, full_screen, screen, 640,480)        
        # self.render_surface = self.screen if render_surface is None else render_surface
        # Set up the window
        pygame.display.set_caption("Pygame + Box2D")

        # Initialize variables for the progress bar
        self.progress_bar_length = 400
        self.progress_bar_height = 30
        self.progress_bar_x = (self.window_width - self.progress_bar_length) // 2
        self.progress_bar_y = 50
        self.elapsed_time = 0
        self.total_time = 10
        self.border_thickness = 4

        # Set up Box2D world
        self.world = b2World(gravity=(0, 8), doSleep=True)  # Note: I changed the gravity to act upwards for this example

        # Create a static body for mouse joint
        self.anchor_body = self.world.CreateStaticBody(position=(0, 0))

        # Set up plank
        self.plank_width, self.plank_height = 400, 20
        self.plank_body = self.world.CreateDynamicBody(  # Changed to CreateDynamicBody
            position=(self.window_width / 2, self.window_height / 2),
            angle=random.uniform(0, math.pi / 2)- math.pi / 4,
            fixtures=b2FixtureDef(
                shape=b2PolygonShape(box=(self.plank_width / 2, self.plank_height / 2)),
                density=1.0,
                friction=0.3,
            ),
            userData="plank"
        )

        # Create anchor point for revolute joint (the pivot point)
        self.anchor_point = self.world.CreateStaticBody(
            position=(self.window_width / 2, self.window_height / 2),
        )

        # Create a revolute joint between the plank and the anchor point
        self.world.CreateRevoluteJoint(
            bodyA=self.anchor_point,
            bodyB=self.plank_body,
            anchor=(self.window_width / 2, self.window_height / 2),
        )

        # Set up ball
        self.ball_radius = 20
        self.ball_body = self.world.CreateDynamicBody(
            position=(self.window_width / 2, 50),
            angle=0.0,
            fixtures=b2FixtureDef(
                shape=b2CircleShape(radius=self.ball_radius),
                density=1.0,
                friction=0.3,
            ),
        )

        self.game_started = False
        # Set up mouse joint
        self.mouse_joint = None

        # Game loop
        self.score = 0

        # Game loop
        self.running = True
        self.font = pygame.font.Font(None, 36)  # Set up font for score display
        self.font2 = pygame.font.Font(None, 100)  # Set up font for score display
        self.start_ticks = pygame.time.get_ticks()  # starter tick
        self.start_time = time.time()
        self.last_time = time.time()
        self.game_started = False
        self.clock = pygame.time.Clock()
        self.fps_last_time = time.time()
        self.frame_count = 0
        self.fps = 0
        
    def init_graphics(self, init_pygame, full_screen, screen, width, height):
        self.init_pygame = init_pygame
        if init_pygame:
            pygame.init()
            self.full_screen = full_screen 
            
            # Setup screen
            info = pygame.display.Info()
            if self.full_screen:
                self.window_width = info.current_w
                self.window_height = info.current_h
                self.render_surface = pygame.display.set_mode((self.window_width, self.window_height), pygame.FULLSCREEN)    
            else:
                self.window_width = width
                self.window_height = height
                self.render_surface = pygame.display.set_mode((self.window_width, self.window_height))
        else:
            self.render_surface = screen
            self.window_width = screen.get_width()
            self.window_height = screen.get_height()  

    def draw_text_with_outline(self, x, y, text, text_color=(255,255,255), outline_color=(0,0,0), outline_thickness=2, alpha_value=255, font=None):
        # Create text surface
        text_surface = font.render(text, True, text_color)
        text_rect = text_surface.get_rect(top=y, left=x)
        
        # Create outline by drawing text multiple times around the original text
        outline_alpha_color = (*outline_color[:3], alpha_value)
        for i in range(-outline_thickness, outline_thickness+1):
            for j in range(-outline_thickness, outline_thickness+1):
                outline_surface = font.render(text, True, outline_alpha_color)
                outline_rect = outline_surface.get_rect(top=y+j, left=x+i)
                self.render_surface.blit(outline_surface, outline_rect)
        
        # Draw the original text
        self.render_surface.blit(text_surface, text_rect) 

    def run_game(self):
        while self.running:
            self.draw_game()
            # Update the display
            pygame.display.flip()

        return int(self.score)
    
    def display_fps(self, screen, fps):
        font = pygame.font.Font(None, 36)
        fps_text = font.render(f"FPS: {int(fps)}", True, (255, 255, 255))
        screen.blit(fps_text, (screen.get_width() - fps_text.get_width() - 10, 10))

    def draw_game(self, mini_game_events = None):            
        current_time = time.time()
        # dt = self.clock.tick(60) / 10.0 
        self.elapsed_time = current_time - self.start_time

        # Break the loop if the game time is up
        if self.elapsed_time >= self.total_time:
            self.running = False
            return False, int(self.score)

        self.render_surface.fill((100, 100, 100))
        seconds = int(current_time - self.start_time)

        # Handle events
        if seconds > 3:
            for event in mini_game_events if mini_game_events else pygame.event.get():
                if event.type == QUIT:
                    self.running = False
                elif event.type == MOUSEBUTTONDOWN:
                    if self.mouse_joint is None:
                        mouse_x, mouse_y = event.pos[0], event.pos[1]
                        self.mouse_joint = self.world.CreateMouseJoint(
                            bodyA=self.anchor_body,
                            bodyB=self.plank_body,
                            target=(mouse_x, mouse_y),
                            maxForce=3000.0 * self.plank_body.mass  # Increased maxForce
                        )
                        self.plank_body.awake = True
                elif event.type == MOUSEBUTTONUP:
                    if self.mouse_joint:
                        self.world.DestroyJoint(self.mouse_joint)
                        self.mouse_joint = None

        if self.mouse_joint:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            self.mouse_joint.target = b2Vec2(mouse_x, mouse_y)


        # Draw plank
        plank_pos = self.plank_body.position
        plank_angle = self.plank_body.angle
        plank_vertices = [
            (int(plank_pos.x + x * cos(plank_angle) - y * sin(plank_angle)),
                int(plank_pos.y + x * sin(plank_angle) + y * cos(plank_angle)))
            for x, y in [(-self.plank_width / 2, -self.plank_height / 2),
                            (self.plank_width / 2, -self.plank_height / 2),
                            (self.plank_width / 2, self.plank_height / 2),
                            (-self.plank_width / 2, self.plank_height / 2)]
        ]
        pygame.draw.polygon(self.render_surface, (0, 0, 255), plank_vertices)

        # Draw ball
        ball_pos = self.ball_body.position
        ball_angle = self.ball_body.angle
        ball_center = (int(ball_pos.x), int(ball_pos.y))
        pygame.draw.circle(self.render_surface, (255, 0, 0), ball_center, self.ball_radius)

        # Check if ball is out of the screen
        if ball_pos.x < 0 or ball_pos.x > self.window_width or ball_pos.y < 0 or ball_pos.y > self.window_height:
            self.running = False  # End the game

        # Draw triangle under the plank in the middle to indicate the center
        anchor_x, anchor_y = self.anchor_point.position
        triangle_height = 30  # Height of the triangle
        triangle_base = 20  # Base of the triangle
        triangle_vertices = [
            (anchor_x - triangle_base // 2, anchor_y + triangle_height // 2),
            (anchor_x + triangle_base // 2, anchor_y + triangle_height // 2),
            (anchor_x, anchor_y - triangle_height // 2),
        ]
        pygame.draw.polygon(self.render_surface, (0, 255, 0), triangle_vertices)  # Draw the triangle in green

        if seconds < 3:
            #countdown_text = self.font2.render(str(3 - seconds) + "...", 1, (255, 255, 255))
            self.draw_text_with_outline(self.window_width // 2, self.window_height // 4, str(3 - seconds) + "...", (255, 255, 255), (0,0,0), 2, 255, self.font2)                
            #self.render_surface.blit(countdown_text, (self.window_width // 2, self.window_height // 4))
        elif seconds == 3:
            #countdown_text = self.font2.render("Ready!", 1, (255, 255, 255))
            self.draw_text_with_outline(self.window_width // 2 - 100, self.window_height // 4, "Ready!", (255, 255, 255), (0,0,0), 2, 255, self.font2)                

            #self.render_surface.blit(countdown_text, (self.window_width // 2 - 100, self.window_height // 4))
        else:
            # Step the simulation
            #time_step = 1.0 / 60.0
            velocity_iterations = 6
            position_iterations = 2
            frame_time =(current_time - self.last_time) * 10
            
            if current_time - self.fps_last_time >= 1:
                self.fps = self.frame_count
                self.frame_count = 0 
                self.fps_last_time = current_time
            self.frame_count += 1

            self.display_fps(self.render_surface, self.fps)                


            self.world.Step(frame_time,1,1)
            self.last_time = current_time
            self.game_started = True
            # Apply gravity manually to the ball
            # self.ball_body.ApplyForceToCenter((0, 500 * self.ball_body.mass), True)
            # Calculate score based on proximity to center
            ball_pos = self.ball_body.position
            anchor_pos = self.anchor_point.position
            distance_to_center = ((ball_pos.x - anchor_pos.x) ** 2 + (ball_pos.y - anchor_pos.y) ** 2) ** 0.5
            # Normalize the distance if needed
            normalized_distance = distance_to_center / (self.plank_width / 2)

            if normalized_distance < 1:
                # Update the score
                self.score += (1 - normalized_distance) * (1 - normalized_distance)  # Or use normalized_distance instead of distance_to_center

            # Display score
            # score_text = self.font.render("Score: {:.2f}".format(self.score), 1, (0, 0, 0))
            # self.render_surface.blit(score_text, (10, 10))  # Display score at the top-left corner
            self.draw_text_with_outline(10, 10, "Score: {:.2f}".format(self.score), (255, 255, 255), (0,0,0), 2, 255, self.font)
            # Calculate progress bar width
            progress_width = int((self.elapsed_time / self.total_time) * self.progress_bar_length)

            # Draw border
            pygame.draw.rect(
                self.render_surface,
                (255, 255, 255),
                (
                    self.progress_bar_x - self.border_thickness,
                    self.progress_bar_y - self.border_thickness,
                    self.progress_bar_length + 2 * self.border_thickness,
                    self.progress_bar_height + 2 * self.border_thickness
                )
            )

            # Draw empty progress bar
            pygame.draw.rect(
                self.render_surface,
                (0, 0, 0),
                (self.progress_bar_x, self.progress_bar_y, self.progress_bar_length, self.progress_bar_height)
            )

            # Draw filled progress bar
            pygame.draw.rect(
                self.render_surface,
                (0, 255, 0),
                (self.progress_bar_x, self.progress_bar_y, progress_width, self.progress_bar_height)
            )


        # Clean up
        return self.running, int(self.score)

if __name__ == "__main__":
    game = PlankAndBall()
    score = game.run_game()
    print("Final score:", score)