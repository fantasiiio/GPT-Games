import math
import pygame
import sys
from Vector2D import Vector2D
from intersect import find_circle_collision_time, line_circle_nearest_point, edge_intersection

# Initialize 
pygame.init()
screen_width = 1000
screen_height = 600
screen = pygame.display.set_mode((screen_width,screen_height))
clock = pygame.time.Clock()


class Ball():
    def __init__(self, position, radius):
        self.position = position
        self.last_position = position
        self.velocity = Vector2D(0,0)
        self.radius = radius

    def draw(self):
        pygame.draw.circle(screen, (255,0,0), (self.position.x, self.position.y), self.radius)

    def update(self):
        pass
        #self.velocity += Vector2D(0, 0.5)

class OBB():
    def __init__(self, center, width, height, angle=0):
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

    def update_edges(self):
        self.edges = []
        for i in range(4):
            p1 = self.corners[i]
            p2 = self.corners[(i+1) % 4]
            self.edges.append((p1, p2))

    def ball_intersection(self, ball):
        
        for edge in self.edges:
            nearest1, line_normal = line_circle_nearest_point(edge[0], edge[1], ball.position, ball.radius)
            nearest2 = ball.last_position + line_normal * ball.radius
            intersect_point = edge_intersection(nearest1, nearest2, edge[0], edge[1])
            if intersect_point:
                intersect_vec = Vector2D(intersect_point[0], intersect_point[1])
                pygame.draw.circle(screen, (0,255,0), (int(intersect_point[0]), int(intersect_point[1])),  5)
                pygame.draw.line(screen, (0,255,0), (int(intersect_vec.x), int(intersect_vec.y)), (int(intersect_vec.x + line_normal.x * 100), int(intersect_vec.y + line_normal.y * 100)), 5)
 
                ball.position = intersect_vec - line_normal * (ball.radius+0.1)
                ball.velocity = ball.velocity.reflect(line_normal)
                ball.position += ball.velocity
                return True

        for corner in self.corners:
            collision_time = find_circle_collision_time(
                ball.last_position, ball.velocity, ball.radius,
                corner, Vector2D(0, 0), 0  # Assuming corner is stationary and has zero radius
            )
            if collision_time and collision_time < 1:
                # Handle the collision (update ball's position and velocity)
                ball.position = ball.last_position + ball.velocity * (collision_time - 0.1)
                collision_normal = (ball.velocity).normalize()
                ball.velocity = ball.velocity.reflect(collision_normal)  # Assuming simple reflection
                return True

       


    @property
    def center(self):
        return self._center
    
    @center.setter
    def center(self, value):
        self._center
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
        pygame.draw.polygon(screen, (255,255,255), corners_tuple)


ball = Ball(Vector2D(screen_width/2,100), 20)
ball.velocity = Vector2D(0,0)

plank_width = 300
box = OBB(Vector2D(screen_width/2, (screen_height /4)*3), 300, 100, 10)

ball.velocity = Vector2D(30,30)
while True:
    screen.fill((0,0,0)) 

    # Check for input
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    
    box.update_edges()
    # Move the ball
    ball.position += ball.velocity
    
    # Bounce off edges 
    if ball.position.x < ball.radius:
        ball.position.x = ball.radius
        ball.velocity = ball.velocity.reflect(Vector2D(1,0))
    elif ball.position.x > screen_width - ball.radius:
        ball.position.x = screen_width - ball.radius    
        ball.velocity = ball.velocity.reflect(Vector2D(-1,0))
    
    if ball.position.y < ball.radius:
        ball.position.y = ball.radius
        ball.velocity = ball.velocity.reflect(Vector2D(0,-1))
    elif ball.position.y > screen_height - ball.radius:    
        ball.position.y = screen_height - ball.radius
        ball.velocity = ball.velocity.reflect(Vector2D(0,1))

    # Get mouse position
    mouse_x, mouse_y = pygame.mouse.get_pos()

    # Calculate angle relative to OBB center
    angle = mouse_x / 10 -45

    # Update the angle of the OBB
    box.angle = angle

    box.ball_intersection(ball)

    ball.last_position = ball.position


    ball.update()
    ball.draw()
    box.draw()
    pygame.display.update()
    
    clock.tick(60)