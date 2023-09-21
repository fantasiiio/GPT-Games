import pygame
import pymunk
import pymunk.pygame_util

# Pygame initialization
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ragdoll Physics Side View")
clock = pygame.time.Clock()
draw_options = pymunk.pygame_util.DrawOptions(screen)

# Pymunk initialization
space = pymunk.Space()
space.gravity = (0, 900)  # Gravity pushing downwards

def create_ragdoll(space):
    body_shapes = []
    ragdoll_group = 1

    # Head
    head_radius = 25
    head_mass = 10
    head_moment = pymunk.moment_for_circle(head_mass, 0, head_radius)
    head = pymunk.Body(head_mass, head_moment)
    head.position = (WIDTH // 2, HEIGHT // 2 + head_radius + 120)  # Positioned higher to give space for other parts
    head_shape = pymunk.Circle(head, head_radius)
    head_shape.group = ragdoll_group
    space.add(head, head_shape)
    body_shapes.append(head_shape)

    # Torso
    torso_length = 80
    torso_width = 20  # Narrower for side view
    torso_mass = 30
    torso_moment = pymunk.moment_for_box(torso_mass, (torso_width, torso_length))
    torso = pymunk.Body(torso_mass, torso_moment)
    torso.position = (WIDTH // 2, HEIGHT // 2 + 40)  # Adjusted position for side view
    torso_shape = pymunk.Poly.create_box(torso, (torso_width, torso_length))
    torso_shape.group = ragdoll_group
    space.add(torso, torso_shape)
    body_shapes.append(torso_shape)

    # Upper Arm
    upper_arm_length = 40
    upper_arm_width = 15
    upper_arm_mass = 10
    upper_arm_moment = pymunk.moment_for_box(upper_arm_mass, (upper_arm_width, upper_arm_length))
    upper_arm = pymunk.Body(upper_arm_mass, upper_arm_moment)
    upper_arm.position = (WIDTH // 2 - torso_width/2 - upper_arm_width/2, head.position[1] - head_radius - upper_arm_length/2)
    upper_arm_shape = pymunk.Poly.create_box(upper_arm, (upper_arm_width, upper_arm_length))
    upper_arm_shape.group = ragdoll_group
    space.add(upper_arm, upper_arm_shape)
    body_shapes.append(upper_arm_shape)

    # Lower Arm
    lower_arm_length = 40
    lower_arm_width = 13
    lower_arm_mass = 8
    lower_arm_moment = pymunk.moment_for_box(lower_arm_mass, (lower_arm_width, lower_arm_length))
    lower_arm = pymunk.Body(lower_arm_mass, lower_arm_moment)
    lower_arm.position = (upper_arm.position[0], upper_arm.position[1] - upper_arm_length/2 - lower_arm_length/2)
    lower_arm_shape = pymunk.Poly.create_box(lower_arm, (lower_arm_width, lower_arm_length))
    lower_arm_shape.group = ragdoll_group
    space.add(lower_arm, lower_arm_shape)
    body_shapes.append(lower_arm_shape)

    # Upper Leg
    upper_leg_length = 50
    upper_leg_width = 18
    upper_leg_mass = 12
    upper_leg_moment = pymunk.moment_for_box(upper_leg_mass, (upper_leg_width, upper_leg_length))
    upper_leg = pymunk.Body(upper_leg_mass, upper_leg_moment)
    upper_leg.position = (WIDTH // 2, torso.position[1] + torso_length/2 + upper_leg_length/2)
    upper_leg_shape = pymunk.Poly.create_box(upper_leg, (upper_leg_width, upper_leg_length))
    upper_leg_shape.group = ragdoll_group
    space.add(upper_leg, upper_leg_shape)
    body_shapes.append(upper_leg_shape)

    # Lower Leg
    lower_leg_length = 50
    lower_leg_width = 16
    lower_leg_mass = 10
    lower_leg_moment = pymunk.moment_for_box(lower_leg_mass, (lower_leg_width, lower_leg_length))
    lower_leg = pymunk.Body(lower_leg_mass, lower_leg_moment)
    lower_leg.position = (upper_leg.position[0], upper_leg.position[1] + upper_leg_length/2 + lower_leg_length/2)
    lower_leg_shape = pymunk.Poly.create_box(lower_leg, (lower_leg_width, lower_leg_length))
    lower_leg_shape.group = ragdoll_group
    space.add(lower_leg, lower_leg_shape)
    body_shapes.append(lower_leg_shape)

    # Joints
    neck_joint = pymunk.PivotJoint(head, torso, (WIDTH // 2, head.position[1] - head_radius))
    shoulder_joint = pymunk.PivotJoint(upper_arm, torso, upper_arm.position + (0, upper_arm_length/2))
    elbow_joint = pymunk.PivotJoint(upper_arm, lower_arm, upper_arm.position + (0, -upper_arm_length/2))
    hip_joint = pymunk.PivotJoint(torso, upper_leg, upper_leg.position + (0, -upper_leg_length/2))
    knee_joint = pymunk.PivotJoint(upper_leg, lower_leg, upper_leg.position + (0, upper_leg_length/2))

    space.add(neck_joint, shoulder_joint, elbow_joint, hip_joint, knee_joint)

    return body_shapes

def create_floor(space):
    # Ground parameters
    ground_thickness = 10
    ground_y = HEIGHT - ground_thickness/2  # Positioned at the bottom of the screen
    
    # Static body represents the ground
    ground = pymunk.Body(body_type=pymunk.Body.STATIC)
    ground_shape = pymunk.Segment(ground, (0, ground_y), (WIDTH, ground_y), ground_thickness/2)
    space.add(ground, ground_shape)  # Adding both body and shape at the same time
    return ground_shape


shapes = create_ragdoll(space)
create_floor(space)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update physics
    space.step(1/60.0)
    
    # Draw everything
    screen.fill((255, 255, 255))
    space.debug_draw(draw_options)
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
