import pygame
from pygame.locals import *
from Box2D import *
from Box2D.b2 import *
from math import sin, cos
import random
import math
import time
# Initialize Pygame
pygame.init()

# Set up the window
window_width, window_height = 800, 600
screen = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption("Pygame + Box2D")

# Initialize variables for the progress bar
progress_bar_length = 400
progress_bar_height = 30
progress_bar_x = (window_width - progress_bar_length) // 2
progress_bar_y = 50
elapsed_time = 0
total_time = 10
border_thickness = 4

# Set up Box2D world
world = b2World(gravity=(0, 0), doSleep=True)  # Note: I changed the gravity to act upwards for this example

# Create a static body for mouse joint
anchor_body = world.CreateStaticBody(position=(0, 0))

# Set up plank
plank_width, plank_height = 400, 20
plank_body = world.CreateDynamicBody(  # Changed to CreateDynamicBody
    position=(window_width / 2, window_height / 2),
    angle=random.uniform(0, math.pi / 2),
    fixtures=b2FixtureDef(
        shape=b2PolygonShape(box=(plank_width / 2, plank_height / 2)),
        density=1.0,
        friction=0.3,
    ),
    userData="plank"
)

# Create anchor point for revolute joint (the pivot point)
anchor_point = world.CreateStaticBody(
    position=(window_width / 2, window_height / 2),
)

# Create a revolute joint between the plank and the anchor point
world.CreateRevoluteJoint(
    bodyA=anchor_point,
    bodyB=plank_body,
    anchor=(window_width / 2, window_height / 2),
)

# Set up ball
ball_radius = 20
ball_body = world.CreateDynamicBody(
    position=(window_width / 2, 50),
    angle=0.0,
    fixtures=b2FixtureDef(
        shape=b2CircleShape(radius=ball_radius),
        density=1.0,
        friction=0.3,
    ),
)


ball_body = world.CreateDynamicBody(
    position=(window_width / 2, 50),
    angle=0.0,
    fixtures=b2FixtureDef(
        shape=b2CircleShape(radius=ball_radius),
        density=1.0,
        friction=0.3,
    )
)

game_started = False
# Set up mouse joint
mouse_joint = None

# Game loop
score = 0

# Game loop
running = True
font = pygame.font.Font(None, 36)  # Set up font for score display
font2 = pygame.font.Font(None, 100)  # Set up font for score display
start_ticks = pygame.time.get_ticks()  # starter tick
start_time = time.time()
game_started = False
while running:
    current_time = time.time()
    elapsed_time = current_time - start_time

    # Break the loop if the game time is up
    if elapsed_time >= total_time:
        running = False
        continue

    screen.fill((255, 255, 255))
    seconds = (pygame.time.get_ticks() - start_ticks) // 1000  

    # Handle events
    if seconds > 3:    
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == MOUSEBUTTONDOWN:
                if mouse_joint is None:
                    mouse_x, mouse_y = event.pos[0], event.pos[1]
                    mouse_joint = world.CreateMouseJoint(
                        bodyA=anchor_body,
                        bodyB=plank_body,
                        target=(mouse_x, mouse_y),
                        maxForce=3000.0 * plank_body.mass  # Increased maxForce
                    )
                    plank_body.awake = True
            elif event.type == MOUSEBUTTONUP:
                if mouse_joint:
                    world.DestroyJoint(mouse_joint)
                    mouse_joint = None

    if mouse_joint:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        mouse_joint.target = b2Vec2(mouse_x, mouse_y)

    # Step the simulation
    time_step = 1.0 / 60.0
    velocity_iterations = 6
    position_iterations = 2
    world.Step(time_step, velocity_iterations, position_iterations)

    # Draw plank
    plank_pos = plank_body.position
    plank_angle = plank_body.angle
    plank_vertices = [
        (int(plank_pos.x + x * cos(plank_angle) - y * sin(plank_angle)),
         int(plank_pos.y + x * sin(plank_angle) + y * cos(plank_angle)))
        for x, y in [(-plank_width / 2, -plank_height / 2),
                     (plank_width / 2, -plank_height / 2),
                     (plank_width / 2, plank_height / 2),
                     (-plank_width / 2, plank_height / 2)]
    ]
    pygame.draw.polygon(screen, (0, 0, 255), plank_vertices)

    # Draw ball
    ball_pos = ball_body.position
    ball_angle = ball_body.angle
    ball_center = (int(ball_pos.x), int(ball_pos.y))
    pygame.draw.circle(screen, (255, 0, 0), ball_center, ball_radius)

    # Draw triangle under the plank in the middle to indicate the center
    anchor_x, anchor_y = anchor_point.position
    triangle_height = 30  # Height of the triangle
    triangle_base = 20  # Base of the triangle
    triangle_vertices = [
        (anchor_x - triangle_base // 2, anchor_y + triangle_height // 2),
        (anchor_x + triangle_base // 2, anchor_y + triangle_height // 2),
        (anchor_x, anchor_y - triangle_height // 2),
    ]
    pygame.draw.polygon(screen, (0, 255, 0), triangle_vertices)  # Draw the triangle in green

    if seconds < 3:
        countdown_text = font2.render(str(3 - seconds) + "...", 1, (0, 0, 0))
        screen.blit(countdown_text, (window_width // 2, window_height // 4))
    elif seconds == 3:
        countdown_text = font2.render("Ready!", 1, (0, 0, 0))
        screen.blit(countdown_text, (window_width // 2 - 100, window_height // 4))
    else:
        if not game_started:
            start_time = time.time()
        game_started = True
        # Apply gravity manually to the ball
        ball_body.ApplyForceToCenter((0, 2 * ball_body.mass), True)
        # Calculate score based on proximity to center
        ball_pos = ball_body.position
        anchor_pos = anchor_point.position
        distance_to_center = ((ball_pos.x - anchor_pos.x) ** 2 + (ball_pos.y - anchor_pos.y) ** 2) ** 0.5
        # Normalize the distance if needed
        normalized_distance = distance_to_center / (plank_width / 2)

        if normalized_distance < 1:
            # Update the score
            score += (1 - normalized_distance)*(1 - normalized_distance)  # Or use normalized_distance instead of distance_to_center

        # Display score
        score_text = font.render("Score: {:.2f}".format(score), 1, (0, 0, 0))
        screen.blit(score_text, (10, 10))  # Display score at the top-left corner

        # Calculate progress bar width
        progress_width = int((elapsed_time / total_time) * progress_bar_length)

        # Draw border
        pygame.draw.rect(
            screen,
            (255, 255, 255),
            (
                progress_bar_x - border_thickness,
                progress_bar_y - border_thickness,
                progress_bar_length + 2 * border_thickness,
                progress_bar_height + 2 * border_thickness
            )
        )

        # Draw empty progress bar
        pygame.draw.rect(
            screen,
            (0, 0, 0),
            (progress_bar_x, progress_bar_y, progress_bar_length, progress_bar_height)
        )

        # Draw filled progress bar
        pygame.draw.rect(
            screen,
            (0, 255, 0),
            (progress_bar_x, progress_bar_y, progress_width, progress_bar_height)
        )

    # Update the display
    pygame.display.flip()

# Clean up
pygame.quit()




import pygame
from pygame.locals import *
from Box2D import *
from Box2D.b2 import *
import random
import math
import time

class PlankAndBall:
    def __init__(self):
        pygame.init()
        self.window_width, self.window_height = 800, 600
        self.screen = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption("Pygame + Box2D")
        self.world = b2World(gravity=(0, 0), doSleep=True)
        self.score = 0
        self.elapsed_time = 0
        self.total_time = 10
        self.progress_bar_length = 400
        self.progress_bar_height = 30
        self.progress_bar_x = (self.window_width - self.progress_bar_length) // 2
        self.progress_bar_y = 50
        self.border_thickness = 4
        self.anchor_body = self.world.CreateStaticBody(position=(0, 0))
        self.plank_body = self.create_plank()
        self.anchor_point = self.create_anchor_point()
        self.world.CreateRevoluteJoint(bodyA=self.anchor_point, bodyB=self.plank_body, anchor=(self.window_width / 2, self.window_height / 2))
        self.ball_body = self.create_ball()
        self.game_started = False
        self.mouse_joint = None
        self.font = pygame.font.Font(None, 36)
        self.font2 = pygame.font.Font(None, 100)
        self.start_time = time.time()
        
    def create_plank(self):
        plank_width, plank_height = 400, 20
        return self.world.CreateDynamicBody(
            position=(self.window_width / 2, self.window_height / 2),
            angle=random.uniform(0, math.pi / 2),
            fixtures=b2FixtureDef(
                shape=b2PolygonShape(box=(plank_width / 2, plank_height / 2)),
                density=1.0,
                friction=0.3,
            )
        )

    def create_anchor_point(self):
        return self.world.CreateStaticBody(
            position=(self.window_width / 2, self.window_height / 2),
        )

    def create_ball(self):
        ball_radius = 20
        return self.world.CreateDynamicBody(
            position=(self.window_width / 2, 50),
            angle=0.0,
            fixtures=b2FixtureDef(
                shape=b2CircleShape(radius=ball_radius),
                density=1.0,
                friction=0.3,
            )
        )
    
    def run(self):
        start_ticks = pygame.time.get_ticks()
        running = True
        while running:
            current_time = time.time()
            self.elapsed_time = current_time - self.start_time

            # ... (skipping drawing and event code for brevity, just paste them here)
            # You can refer to your previous code for drawing the plank, ball, score, progress bar, etc.

if __name__ == '__main__':
    game = PlankAndBall()
    game.run()

