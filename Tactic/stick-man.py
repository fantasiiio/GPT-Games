import math
import pygame
import sys
import Box2D  # The main library
from Box2D.b2 import (world, polygonShape, circleShape, staticBody, dynamicBody)
from Box2D import b2Vec2, b2World, b2PolygonShape, b2CircleShape, b2RevoluteJointDef, b2_dynamicBody, b2_staticBody

# Player settings
player_height = 600
player_width = 100
player_speed = 5
head_radius = 80
half_arm_length = 170
half_leg_length = 230
body_height = 300
feet_length = 50
glove_size = 40
feet_distance = 100
floor_height = 100
feet_left_pos = 100
thickness = 60
glove_color = (150,0,0)

# Initialize 
pygame.init()
screen_width = 1000
screen_height = 1000
screen = pygame.display.set_mode((screen_width,screen_height))
clock = pygame.time.Clock()

# Initialize Box2D world
gravity = (0, -10)
world = world(gravity=gravity)


class Ball():
    def __init__(self, position, radius, color=(0,0,0)):
        self.color = color
        self.body = world.CreateDynamicBody(
            position=position,
            type=b2_dynamicBody
        )
        self.body.CreateCircleFixture(radius=radius/30, density=1, friction=0.3)  # Create a Box2D circle shape
        self.radius = radius

    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.body.position.x * 30), int(self.body.position.y * 30)), self.radius)


class OBB():
    def __init__(self, center, width, height, angle=0, color=(0,0,0)):
        self.color = color
        self.width = width
        self.height = height
        #self.angle = angle
        self.center = b2Vec2(center[0], center[1])  # Use b2Vec2 here
        self.body = world.CreateDynamicBody(
            position=self.center,
            angle=math.radians(angle),
            type=b2_dynamicBody
        )
        self.body.CreatePolygonFixture(box=(self.width/30, self.height/30), density=1, friction=0.3)  # Create a Box2D box shape

    def draw(self):
        corners = [(self.body.transform * v) for v in self.body.fixtures[0].shape.vertices]
        pygame.draw.polygon(screen, self.color, [(point[0] * 30, point[1] * 30) for point in corners])   


    @property
    def angle(self):
        return self._angle
    
    @angle.setter
    def angle(self, value):
        self._angle = value
        self.update_corners()

    def draw(self):
        # Get the fixture and shape from the Box2D body
        fixture = self.body.fixtures[0]
        shape = fixture.shape

        # Convert vertices to screen coordinates and make them into tuples
        corners_tuple = [(v[0] * 30, v[1] * 30) for v in shape.vertices]

        pygame.draw.polygon(screen, self.color, corners_tuple)



class Capsule:
    def __init__(self, center, length, thickness=20, angle=0):
        self.center = center
        self.length = length
        self.thickness = thickness
        #self.angle = angle

        # Create the OBB (box) using the OBB class
        self.obb = OBB(center, self.length, self.thickness, angle)

        # Calculate the positions for the balls at each end (centered on the edges)
        delta = b2Vec2(math.cos(math.radians(angle)), math.sin(math.radians(angle))) * (self.length / 2)
        ball1_pos = b2Vec2(self.center.x - delta.x, self.center.y - delta.y)
        ball2_pos = b2Vec2(self.center.x + delta.x, self.center.y + delta.y)

        # Create the balls using the Ball class
        self.ball1 = Ball(ball1_pos, self.thickness / 2)
        self.ball2 = Ball(ball2_pos, self.thickness / 2)

        # Create joints to connect balls to the OBB
        joint_def = b2RevoluteJointDef(
            bodyA=self.obb.body,
            bodyB=self.ball1.body,
            localAnchorA=delta,
            localAnchorB=(0, 0)
        )
        self.joint1 = world.CreateJoint(joint_def)

        joint_def.bodyB = self.ball2.body
        joint_def.localAnchorA = -delta
        self.joint2 = world.CreateJoint(joint_def)

    def draw(self):
        self.obb.draw()
        self.ball1.draw()
        self.ball2.draw()

    def update(self):
        # Fetch and store the latest positions and angles from the Box2D bodies
        self.center = self.obb.body.position
        # self.angle = math.degrees(self.obb.body.angle)

    @classmethod
    def from_start_end(cls, start_pos, end_pos, radius=20):
        angle = math.degrees(math.atan2(end_pos.y - start_pos.y, end_pos.x - start_pos.x))
        distance = start_pos.distance_to(end_pos)
        center = (start_pos + end_pos) / 2
        length = distance
        return cls(center, length, thickness=radius, angle=angle)

    @classmethod
    def from_start_angle_distance(cls, start_pos, angle, distance, radius=20):
        end_pos = start_pos + b2Vec2(math.cos(math.radians(angle)), math.sin(math.radians(angle))) * distance
        center = (start_pos + end_pos) / 2
        length = distance
        return cls(center, length, thickness=radius, angle=angle)



# Example usage:

# Initialize a Capsule with center at (500, 300), width 100, height 40, and angle 30 degrees



left_feet = None
right_feet = None
left_leg = None
left_leg2 = None
right_leg = None
right_leg2 = None
arm = None
arm2 = None
glove = None
body = None
head = None

def create_revolute_joint(bodyA, bodyB, anchorA, anchorB):
    joint_def = b2RevoluteJointDef(
        bodyA=bodyA,
        bodyB=bodyB,
        localAnchorA=anchorA,
        localAnchorB=anchorB
    )
    return world.CreateJoint(joint_def)

def init_stick_man():
    global left_feet, right_feet, left_leg, left_leg2, right_leg, right_leg2, arm, arm2, right_arm, right_arm2, body, head, glove

    # Create the body capsule
    body = Capsule(b2Vec2(screen_width / 2, screen_height / 3), body_height, thickness, 90)

    # Create left leg and its joints
    start = body.ball2.body.position
    left_leg = Capsule.from_start_angle_distance(start, 90, half_leg_length, thickness)
    create_revolute_joint(body.obb.body, left_leg.obb.body, b2Vec2(0, -body.length / 2), b2Vec2(0, left_leg.length / 2))

    start = left_leg.ball2.body.position
    angle = 135
    left_leg2 = Capsule.from_start_angle_distance(start, angle, half_leg_length, thickness)
    create_revolute_joint(left_leg.obb.body, left_leg2.obb.body, b2Vec2(0, -left_leg.length / 2), b2Vec2(0, left_leg2.length / 2))

    start = left_leg2.ball2.body.position
    left_feet = Capsule.from_start_angle_distance(start, angle - 90, feet_length, thickness)
    create_revolute_joint(left_leg2.obb.body, left_feet.obb.body, b2Vec2(0, -left_leg2.length / 2), b2Vec2(0, left_feet.length / 2))

    # Create right leg and its joints (similar to left leg)
    start = body.ball2.body.position
    right_leg = Capsule.from_start_angle_distance(start, 0, half_leg_length, thickness)
    create_revolute_joint(body.obb.body, right_leg.obb.body, b2Vec2(0, -body.length / 2), b2Vec2(0, right_leg.length / 2))

    start = right_leg.ball2.body.position
    angle = 45
    right_leg2 = Capsule.from_start_angle_distance(start, angle, half_leg_length, thickness)
    create_revolute_joint(right_leg.obb.body, right_leg2.obb.body, b2Vec2(0, -right_leg.length / 2), b2Vec2(0, right_leg2.length / 2))

    start = right_leg2.ball2.body.position
    right_feet = Capsule.from_start_angle_distance(start, angle - 90, feet_length, thickness)
    create_revolute_joint(right_leg2.obb.body, right_feet.obb.body, b2Vec2(0, -right_leg2.length / 2), b2Vec2(0, right_feet.length / 2))

    # Create arm and its joints
    start = body.ball1.body.position
    arm = Capsule.from_start_angle_distance(start, 45, half_arm_length, thickness)
    create_revolute_joint(body.obb.body, arm.obb.body, b2Vec2(0, body.length / 2), b2Vec2(0, -arm.length / 2))

    start = arm.ball2.body.position
    arm2 = Capsule.from_start_angle_distance(start, -45, half_arm_length, thickness)
    create_revolute_joint(arm.obb.body, arm2.obb.body, b2Vec2(0, arm.length / 2), b2Vec2(0, -arm2.length / 2))

    start = arm2.ball2.body.position
    glove = Ball(start, glove_size, color=glove_color)

    # Create head (assuming you have head_radius and edge_direction variables defined)

    fixture = body.obb.body.fixtures[0]  # Assuming the fixture you're interested in is the first one
    shape = fixture.shape
    # Assuming it's a polygon shape, the vertices can be accessed:
    first_vertex = b2Vec2(*shape.vertices[0])
    second_vertex = b2Vec2(*shape.vertices[1])

    # Calculate the edge direction
    edge_direction = second_vertex - first_vertex
    edge_direction.Normalize()  # Normalize the vector
    start = body.ball1.body.position + edge_direction * head_radius
    head = Ball(start, head_radius, (0, 0, 0))

init_stick_man()

# Create floor (static body)
floor = world.CreateStaticBody(
    position=(screen_width / 2 / 30, (screen_height - floor_height) / 30)
)
floor.CreatePolygonFixture(box=(screen_width / 30, floor_height / 30), density=0, friction=0.3)


timeStep = 1.0 / 60
vel_iters, pos_iters = 10, 10

while True:
    screen.fill((200,200,200)) 

    # Check for input
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()


    world.Step(timeStep, vel_iters, pos_iters)
    
    body.draw()
    left_leg.draw()            
    left_leg2.draw()
    left_feet.draw()

    right_leg.draw()            
    right_leg2.draw()
    right_feet.draw()

    arm.draw()
    arm2.draw()
    glove.draw()
    head.draw()

    # Draw floor
    pygame.draw.rect(screen, (0, 0, 0), (0, screen_height - floor_height, screen_width, floor_height))


    pygame.display.update()
    
    clock.tick(60)