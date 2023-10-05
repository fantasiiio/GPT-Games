from DashedLine import DashedLine
import math
import pygame
import sys
from Vector2D import Vector2D

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
feet_distance = 200
floor_height = 100
feet_left_pos = 100
thickness = 60
glove_color = (150,0,0)
punch_distance = 200
punch_speed = 10

# Initialize 
pygame.init()
screen_width = 1600
screen_height = 1200
screen = pygame.display.set_mode((screen_width,screen_height))
clock = pygame.time.Clock()


class Ball():
    def __init__(self, position, radius, color=(0,0,0)):
        self.color = color
        self.position = position
        self.last_position = position
        self.velocity = Vector2D(0,0)
        self.radius = radius

    def draw(self):
        pygame.draw.circle(screen, self.color, (self.position.x, self.position.y), self.radius)

    def update(self):
        self.velocity += Vector2D(0, 0.5)

class OBB():
    def __init__(self, center, width, height, angle=0, color=(0,0,0)):
        self.color = color
        self.width = width
        self.height = height
        self.half_width = width / 2
        self.half_height = height / 2
        self._angle = angle
        self.corners = []
        self._center = center
        self.corners.append(Vector2D(width/2, height/2).rotate(self.angle) + center)
        self.corners.append(Vector2D(-width/2, height/2).rotate(self.angle) + center)
        self.corners.append(Vector2D(-width/2, -height/2).rotate(self.angle) + center)
        self.corners.append(Vector2D(width/2, -height/2).rotate(self.angle) + center)

        # Get edge vectors
        self.edges = []
        for i in range(4):
            p1 = self.corners[i]
            p2 = self.corners[(i+1) % 4]
            self.edges.append((p1, p2))        

    def update_corners(self):
        self.corners[0] = Vector2D(self.width/2, self.height/2).rotate(self.angle) + self.center
        self.corners[1] = Vector2D(-self.width/2, self.height/2).rotate(self.angle) + self.center
        self.corners[2] = Vector2D(-self.width/2, -self.height/2).rotate(self.angle) + self.center  
        self.corners[3] = Vector2D(self.width/2, -self.height/2).rotate(self.angle) + self.center

       


    @property
    def center(self):
        return self._center
    
    @center.setter
    def center(self, value):
        self._center = value
        self.update_corners()        

    @property
    def angle(self):
        return self._angle
    
    @angle.setter
    def angle(self, value):
        self._angle = value
        self.update_corners()

    def draw(self):
        corners_tuple = [(v.x, v.y) for v in self.corners]
        pygame.draw.polygon(screen, self.color, corners_tuple)


class Capsule():
    def __init__(self, center, length, thickness=20, angle=0):
        self.center = center
        self.length = length
        self.thickness = thickness
        self.angle = angle

        # Initialize the OBB based on the above properties
        self.obb = OBB(self.center, self.length, self.thickness, self.angle)
        
        # Calculate the positions for the balls at each end (centered on the edges)
        delta = Vector2D(math.cos(math.radians(angle)), math.sin(math.radians(angle))) * (self.length / 2)
        ball1_pos = self.center - delta
        ball2_pos = self.center + delta
        
        # Initialize the balls
        self.ball1 = Ball(ball1_pos, thickness / 2)
        self.ball2 = Ball(ball2_pos, thickness / 2)


    @classmethod
    def from_start_end(cls, start_pos, end_pos, radius=20):
        angle = math.degrees(math.atan2(end_pos.y - start_pos.y, end_pos.x - start_pos.x))
        distance = start_pos.distance_to(end_pos)
        center = (start_pos + end_pos) / 2
        length = distance
        return cls(center, length, thickness=radius, angle=angle)

    @classmethod
    def from_start_angle_distance(cls, start_pos, angle, distance, radius=20):
        end_pos = start_pos + Vector2D(math.cos(math.radians(angle)), math.sin(math.radians(angle))) * distance
        center = (start_pos + end_pos) / 2
        length = distance
        return cls(center, length, thickness=radius, angle=angle)

    def update_from_start_angle_distance(self, start_pos, angle, distance):
        end_pos = start_pos + Vector2D(math.cos(math.radians(angle)), math.sin(math.radians(angle))) * distance
        self.update(start_pos, end_pos)

    def update(self, start_point, end_point):
        # Update the start and end points
        self.ball1.position = start_point
        self.ball2.position = end_point
        
        # Recalculate the center of the capsule
        self.center = (start_point + end_point) / 2

        # Recalculate the orientation angle of the capsule
        delta = end_point - start_point
        self.angle = math.degrees(math.atan2(delta.y, delta.x))

        # Recalculate the length of the OBB (subtract twice the radius for the end circles)
        self.length = start_point.distance_to(end_point)
        
        # Update OBB properties
        self.obb.angle = self.angle
        self.obb.width = self.length
        self.obb.height = self.thickness
        self.obb.center = self.center
        #self.obb.update_corners()

        # Update balls (if they have an update method)
        self.ball1.update()
        self.ball2.update()

    def draw(self):
        # Draw OBB and balls
        self.ball1.draw()
        self.ball2.draw()
        self.obb.draw()

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

glove_state = "idle"  # "idle" or "punching"
glove_velocity = Vector2D(0, 0)

def inverse_kinematics(base_vec, target_vec, l1, l2):
    # Compute the vector from base to target
    base_to_target = target_vec - base_vec
    
    # Compute the distance from base to target
    distance = abs(base_to_target)

    # Constrain the total reach
    if distance > l1 + l2:
        direction = base_to_target.normalize()
        base_to_target = direction * (l1 + l2)
        target_vec = base_vec + base_to_target
        distance = l1 + l2

    # Two-link arm inverse kinematics formulae
    #a1 = math.acos((l1 ** 2 + distance ** 2 - l2 ** 2) / (2 * l1 * distance))
   # a2 = math.acos((l1 ** 2 + l2 ** 2 - distance ** 2) / (2 * l1 * l2))
    try:
        a1 = math.acos((l1 ** 2 + distance ** 2 - l2 ** 2) / (2 * l1 * distance))
        a2 = math.acos((l1 ** 2 + l2 ** 2 - distance ** 2) / (2 * l1 * l2))
    except ValueError as e:
        print(f"Math error with base: {base_vec}, target: {target_vec}, l1: {l1}, l2: {l2}, distance: {distance}")
        raise e  # re-raise the exception to see the stack trace

    # Get the angle to target
    angle_to_target = math.atan2(base_to_target.y, base_to_target.x)
    
    # Calculate elbow position
    elbow_direction = Vector2D(math.cos(angle_to_target + a1), math.sin(angle_to_target + a1))
    elbow_vec = base_vec + (elbow_direction * l1)

    # Calculate glove position from the elbow
    elbow_to_target = target_vec - elbow_vec
    glove_direction = elbow_to_target.normalize()
    glove_vec = elbow_vec + (glove_direction * l2)

    return elbow_vec, glove_vec

def init_stick_man():
    global left_feet, left_feet,right_feet,left_leg,left_leg2,right_leg,right_leg2,arm,arm2,right_arm,right_arm2,body,head, glove

    body = Capsule(Vector2D(screen_width/2, screen_height /3), body_height, thickness, 90)

    start = body.ball2.position
    left_leg = Capsule.from_start_angle_distance(start, 90, half_leg_length, thickness)

    start = left_leg.ball2.position
    angle = 135
    left_leg2 = Capsule.from_start_angle_distance(start, angle, half_leg_length, thickness)

    start = left_leg2.ball2.position
    left_feet = Capsule.from_start_angle_distance(start, 0, feet_length,  thickness)

    start = body.ball2.position
    right_leg = Capsule.from_start_angle_distance(start, 0, half_leg_length, thickness)

    start = right_leg.ball2.position
    angle = 45
    right_leg2 = Capsule.from_start_angle_distance(start, angle, half_leg_length, thickness)

    #start = right_leg2.ball2.position
    start = left_feet.ball2.position + Vector2D(feet_distance, 0)
    right_feet = Capsule.from_start_angle_distance(start, 0, feet_length,  thickness)

    start = body.ball1.position
    arm = Capsule.from_start_angle_distance(start, 45, half_arm_length, thickness)

    start = arm.ball2.position
    arm2 = Capsule.from_start_angle_distance(start, -45, half_arm_length, thickness)

    start = arm2.ball2.position
    glove = Ball(start, glove_size, color=glove_color)

    edge_direction = (body.obb.edges[0][1] - body.obb.edges[0][0]).normalize()
    start = body.ball1.position + edge_direction * head_radius
    head = Ball(start, head_radius, (0,0,0))


def is_reachable(target, glove, threshold=1.0):
    return target.distance_to(glove) < threshold


def update_positions(mouse_position, base1, base2, l1, l2, threshold=10):
    target = mouse_position
    while True:
        elbow1, glove1 = inverse_kinematics(base1, target, l1, l2)
        elbow2, glove2 = inverse_kinematics(base2, target, l1, l2)

        delta_glove = (glove1 - glove2)
        delta_len = delta_glove.__abs__()
        if delta_len < threshold:
            break    

        target = glove1 - delta_glove/2
        
    # Recalculate the IK for both arms one final time
    new_elbow1, new_glove1 = inverse_kinematics(base1, target, l1, l2)
    new_elbow2, new_glove2 = inverse_kinematics(base2, target, l1, l2)
    
    return new_elbow1, new_glove1, new_elbow2, new_glove2

move_body_offset = Vector2D(0,0)

def move_stick_man():
    global left_feet, left_feet,right_feet,left_leg,left_leg2,right_leg,right_leg2,arm,arm2,right_arm,right_arm2,body,head, glove

    pos_before = body.ball2.position
    target = Vector2D(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]) + move_body_offset
    start_pos1 = left_feet.ball1.position
    start_pos2 = right_feet.ball1.position
    middle_pos1, end_pos1, middle_pos2, end_pos2 = update_positions(target, start_pos1, start_pos2, half_leg_length, half_leg_length)    

    left_leg2.update(start_pos1, middle_pos1)
    left_leg.update(middle_pos1, end_pos1)

    right_leg2.update(start_pos2, middle_pos2)
    right_leg.update(middle_pos2, end_pos2)

    body.update_from_start_angle_distance(left_leg.ball2.position, 90, -body_height)  

    pos_after = body.ball2.position
    pos_delta = pos_after - pos_before

    arm.update(body.ball2.position, arm.ball2.position + pos_delta)
    arm2.update(arm.ball2.position, arm2.ball2.position + pos_delta)
    glove.position += pos_delta

    # Move the head
    edge_direction = (body.obb.edges[0][1] - body.obb.edges[0][0]).normalize()
    start = body.ball2.position + edge_direction * head_radius
    head.position = start

def move_glove_with_mouse():
    global left_feet, left_feet,right_feet,left_leg,left_leg2,right_leg,right_leg2,arm,arm2,right_arm,right_arm2,body,head, glove

    target = Vector2D(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1])
    start = body.ball2.position
    middle_pos, end_pos = inverse_kinematics(start, target, half_arm_length, half_arm_length)
    arm.update(start, middle_pos)
    arm2.update(middle_pos, end_pos)

    start = arm2.ball2.position
    glove = Ball(start, glove_size, color=glove_color)

def easeInBack(x):
    c1 = 1.70158
    c3 = c1 + 1
    
    return c3 * x * x * x - c1 * x * x

def move_punch(punch_time, punch_distance):
    global glove_state, glove_velocity, glove
    if glove_state == "punching":
        time_scale = easeInBack(punch_time)
        glove.position += glove_velocity

        final_target = Vector2D(body.ball2.position.x + punch_distance + 100, body.ball2.position.y)
        target = Vector2D(body.ball2.position.x + (time_scale * punch_distance) + 100, body.ball2.position.y)
        start = body.ball2.position
        middle_pos, end_pos = inverse_kinematics(start, target, half_arm_length, half_arm_length)
        arm.update(start, middle_pos)
        arm2.update(middle_pos, end_pos)
        start = arm2.ball2.position
        glove = Ball(start, glove_size, color=glove_color)        
        # Stop the punch after reaching a certain distance or another condition
        if glove.position.distance_to(final_target) < punch_speed*5:  # Replace 200 with your desired distance
            start = body.ball2.position
            middle_pos, end_pos = inverse_kinematics(start, final_target, half_arm_length, half_arm_length)
            arm.update(start, middle_pos)
            arm2.update(middle_pos, end_pos)
            start = arm2.ball2.position
            glove = Ball(start, glove_size, color=glove_color)             
            glove_state = "idle"


init_stick_man()
glove_state = "punching"
move_punch(0,0)


lines = []

class Line():
    def __init__(self, start, end):
        self.start = start
        self.end = end

    def draw(self):
        DashedLine.draw(screen, self.start, self.end, 10, (0,0,0), 3)

lines.append(Line(Vector2D(0,0), Vector2D(0,0)))
lines.append(Line(Vector2D(0,0), Vector2D(0,0)))

def update_lines():
    global lines
    target = Vector2D(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1])    
    lines[0].start=target
    lines[0].end=left_leg2.ball2.position
    lines[1].start=target
    lines[1].end=right_leg2.ball2.position

move_body = False
move_arm = False
move_stick_man()
time_punch_started = 0
while True:
    screen.fill((200,200,200)) 
    current_time = pygame.time.get_ticks()
    # Check for input
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # Check for right mouse button press
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pressed = pygame.mouse.get_pressed()
            if mouse_pressed[2]: 
                move_body = True  
                move_body_offset = body.ball1.position - Vector2D(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1])
            elif mouse_pressed[0]:
                move_arm = True
                # New code for left-click (punch)
                if glove_state == "idle":
                    glove_state = "punching"
                    # Set velocity and direction for the punch
                    glove_velocity = Vector2D(10, 0)  # Replace with your desired velocity and direction
                    time_punch_started = pygame.time.get_ticks()

        
        # Check for right mouse button release
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 3:  
                move_body = False  
            elif event.button == 1:  
                move_arm = False

    punch_time = (current_time - time_punch_started) / (1000 / punch_speed)
    move_punch(punch_time, punch_distance)        
    if move_arm:
        move_glove_with_mouse()

    if move_body:
        move_stick_man()

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

    # update_lines()
    # for line in lines:
    #     line.draw()

    pygame.display.update()
    
    clock.tick(60)