import pygame
import sys
import Box2D  # The main library
from Box2D.b2 import (world, polygonShape, circleShape, staticBody, dynamicBody)

# Initialize
pygame.init()
screen_width = 1000
screen_height = 1000
screen = pygame.display.set_mode((screen_width, screen_height))
clock = pygame.time.Clock()

# Initialize Box2D world
gravity = (0, -10)
world = world(gravity=gravity)

# Function to create a Box2D body and associate it with a shape
def create_body(shape, position, body_type=dynamicBody):
    if shape == 'circle':
        shape = circleShape(radius=1)
    elif shape == 'box':
        shape = polygonShape(box=(1, 1))

    body = world.CreateDynamicBody(position=position)
    body.CreateFixture(shape=shape)
    return body

# Create stickman parts as Box2D bodies
head = create_body('circle', (screen_width // 2 / 30, screen_height // 2 / 30))
body = create_body('box', (screen_width // 2 / 30, (screen_height // 2 - 60) / 30))
left_leg = create_body('box', (screen_width // 2 / 30, (screen_height // 2 - 120) / 30))
right_leg = create_body('box', (screen_width // 2 / 30, (screen_height // 2 - 120) / 30))
left_arm = create_body('box', (screen_width // 2 / 30, (screen_height // 2 - 30) / 30))
right_arm = create_body('box', (screen_width // 2 / 30, (screen_height // 2 - 30) / 30))

# Main game loop
while True:
    screen.fill((200, 200, 200))

    # Check for input
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Physics simulation
    world.Step(1 / 60, 10, 10)

    # Draw stickman parts
    pygame.draw.circle(screen, (0, 0, 0), (int(head.position.x * 30), int(head.position.y * 30)), 30)
    pygame.draw.rect(screen, (0, 0, 0), (int(body.position.x * 30) - 15, int(body.position.y * 30) - 30, 30, 60))
    pygame.draw.rect(screen, (0, 0, 0), (int(left_leg.position.x * 30) - 10, int(left_leg.position.y * 30) - 30, 20, 60))
    pygame.draw.rect(screen, (0, 0, 0), (int(right_leg.position.x * 30) - 10, int(right_leg.position.y * 30) - 30, 20, 60))
    pygame.draw.rect(screen, (0, 0, 0), (int(left_arm.position.x * 30) - 10, int(left_arm.position.y * 30) - 20, 20, 40))
    pygame.draw.rect(screen, (0, 0, 0), (int(right_arm.position.x * 30) - 10, int(right_arm.position.y * 30) - 20, 20, 40))

    pygame.display.update()
    clock.tick(60)
