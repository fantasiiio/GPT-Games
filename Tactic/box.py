import pygame
import sys
import math

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 1000, 1000
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2D Boxing Game")

# Colors
RED = (255, 0, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

# Player settings
player_height = 600
player_width = 100
player_speed = 5
head_radius = 80
half_arm_length = 170
half_leg_length = 230
body_height = 300
feet_length = 50
glove_size = 10
feet_distance = 100
floor_height = 100
feet_left_pos = 100

# Initial positions and health
red_pos = [100, HEIGHT // 2]
blue_pos = [WIDTH - 100, HEIGHT // 2]
red_health = 100
blue_health = 100

def inverse_kinematics(base, target, l1, l2):
    dx = target[0] - base[0]
    dy = target[1] - base[1]
    distance = math.sqrt(dx ** 2 + dy ** 2)

    # Constrain the total reach
    if distance > l1 + l2:
        dx *= (l1 + l2) / distance
        dy *= (l1 + l2) / distance
        distance = l1 + l2
        target = (base[0] + dx, base[1] + dy)

    # Two-link arm inverse kinematics formulae
    a1 = math.acos((l1 ** 2 + distance ** 2 - l2 ** 2) / (2 * l1 * distance))
    a2 = math.acos((l1 ** 2 + l2 ** 2 - distance ** 2) / (2 * l1 * l2))

    elbow_x = base[0] + l1 * math.cos(math.atan2(dy, dx) + a1)
    elbow_y = base[1] + l1 * math.sin(math.atan2(dy, dx) + a1)

    # Calculate glove position from the elbow, not the shoulder
    target_dx = target[0] - elbow_x
    target_dy = target[1] - elbow_y

    target_x = elbow_x + l2 * math.cos(math.atan2(target_dy, target_dx))
    target_y = elbow_y + l2 * math.sin(math.atan2(target_dy, target_dx))

    return (elbow_x, elbow_y), (target_x, target_y)


def draw_boxer(pos, color, target):
    pass
    # Left Feet



def draw_floor(height):
    pygame.draw.rect(SCREEN, BLACK, (0, HEIGHT - height, WIDTH, height))

# Main game loop
clock = pygame.time.Clock()
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    keys = pygame.key.get_pressed()
    mouse_x, mouse_y = pygame.mouse.get_pos()

    # Draw everything
    SCREEN.fill(WHITE)

    # Draw Boxers with simple IK
    draw_boxer(red_pos, RED, [mouse_x, mouse_y])
    draw_boxer(blue_pos, BLUE, [mouse_x, mouse_y])
    draw_floor(floor_height)

    pygame.display.flip()
    clock.tick(30)
