from datetime import datetime, timedelta
import json
import threading
import queue
from DashedLine import DashedLine
import math
import pygame
import sys
from Vector2D import Vector2D
from intersect import (
    find_circle_collision_time,
    line_circle_nearest_point,
    edge_intersection,
)
from threading import Thread
from queue import Queue
import pygame
import socket
import struct
from Connection import Connection
from config import *

class HealthBar:
    def __init__(self, max_health, position, color=(0, 255, 0)):
        self.max_health = max_health
        self.current_health = max_health
        self.position = position
        self.width = 200
        self.height = 20
        self.color = (0, 255, 0)

    def draw(self, screen):
        health_percent = self.current_health / self.max_health
        fill_width = int(self.width * health_percent)
        fill_rect = pygame.Rect(
            self.position.x, self.position.y, fill_width, self.height
        )
        outline_rect = pygame.Rect(
            self.position.x, self.position.y, fill_width, self.height
        )
        pygame.draw.rect(screen, self.color, fill_rect)
        pygame.draw.rect(screen, (255, 255, 255), outline_rect, 2)

    def update(self, screen):
        self.draw(screen)

    def take_damage(self, amount):
        self.current_health -= amount
        if self.current_health < 0:
            self.current_health = 0


class Ball:
    def __init__(
        self,
        position,
        radius,
        screen,
        color=(0, 0, 0),
        name="",
        mirror=False,
        owner=None,
    ):
        self.owner = owner
        self.screen = screen
        self.name = name
        self.color = color
        self.position = position
        self.last_position = position
        self.velocity = Vector2D(0, 0)
        self.radius = radius
        self.original_color = color
        self.collision_speed = 0
        self.damage_taken = 0
        self.time_hit = None

    def is_moving_away_or_towards(self, reference_point):
        # Calculate the velocity vector
        velocity = self.velocity

        # Calculate the vector from the reference point to the glove's current position
        current_vector = self.last_position.x + velocity.x - reference_point.x

        # Calculate the vector from the reference point to the glove's last position
        last_vector = self.last_position.x - reference_point.x

        if current_vector > last_vector:
            return 1
        elif current_vector < last_vector:
            return -1

    def update(self):
        self.velocity = self.position - self.last_position
        if self.velocity.__abs__() > 0.0001:
            self.velocity = self.velocity

    def ball_intersection(self, ball):
        if ball.velocity.__abs__() <= 0.0001:
            return False
        collision_time = find_circle_collision_time(
            ball.last_position,
            ball.velocity,
            ball.radius,
            self.last_position,
            self.velocity,
            self.radius,
        )
        direction = ball.is_moving_away_or_towards(self.owner.body.ball2.position)
        if direction == 1 and collision_time and collision_time <= 1:
            # self.color = (255,0, 0)
            # Handle the collision (update self's position and velocity)
            ball.position = ball.last_position + ball.velocity * (collision_time - 0.1)
            # collision_normal = -(ball.velocity).normalize()
            # ball.velocity = ball.velocity.reflect(collision_normal)  # Assuming simple reflection
            if self.name == "head":
                self.take_damage(ball)
            return True
        else:
            self.color = self.original_color

    def draw(self):
        if self.damage_taken > 0:
            hit_force_scale = min(self.damage_taken / max_damage, 1)
            current_time = pygame.time.get_ticks()
            delta_time = (current_time - self.time_hit) / (1000)
            ease = 1 - self.owner.easeInQuint(delta_time)
            red = min(255 * hit_force_scale * ease, 255)
            red = max(red, 0)
            self.color = (red, 0, 0)
            if ease >= 1:
                self.damage_taken = 0
                self.time_hit = None

        pygame.draw.circle(
            self.screen, self.color, (self.position.x, self.position.y), self.radius
        )

    def take_damage(self, ball):
        speed = ball.velocity.__abs__()
        self.damage_taken = speed
        self.time_hit = pygame.time.get_ticks()
        self.owner.health_bar.take_damage(speed)


class OBB:
    def __init__(self, center, width, height, angle=0, color=(0, 0, 0), screen=None):
        self.screen = screen
        self.color = color
        self.original_color = color
        self.width = width
        self.height = height
        self.half_width = width / 2
        self.half_height = height / 2
        self._angle = angle
        self.corners = []
        self._center = center
        self.corners.append(Vector2D(width / 2, height / 2).rotate(self.angle) + center)
        self.corners.append(
            Vector2D(-width / 2, height / 2).rotate(self.angle) + center
        )
        self.corners.append(
            Vector2D(-width / 2, -height / 2).rotate(self.angle) + center
        )
        self.corners.append(
            Vector2D(width / 2, -height / 2).rotate(self.angle) + center
        )

        # Get edge vectors
        self.edges = []
        for i in range(4):
            p1 = self.corners[i]
            p2 = self.corners[(i + 1) % 4]
            self.edges.append((p1, p2))

    def update_corners(self):
        self.corners[0] = (
            Vector2D(self.width / 2, self.height / 2).rotate(self.angle) + self.center
        )
        self.corners[1] = (
            Vector2D(-self.width / 2, self.height / 2).rotate(self.angle) + self.center
        )
        self.corners[2] = (
            Vector2D(-self.width / 2, -self.height / 2).rotate(self.angle) + self.center
        )
        self.corners[3] = (
            Vector2D(self.width / 2, -self.height / 2).rotate(self.angle) + self.center
        )

        # Get edge vectors
        self.edges = []
        for i in range(4):
            p1 = self.corners[i]
            p2 = self.corners[(i + 1) % 4]
            self.edges.append((p1, p2))

    def ball_intersection(self, ball):
        if ball.velocity.__abs__() <= 0.0001:
            return False
        for edge in self.edges:
            nearest1, line_normal = line_circle_nearest_point(
                edge[0], edge[1], ball.position, ball.radius
            )
            nearest2 = ball.last_position + ball.velocity + line_normal * ball.radius
            intersect_point = edge_intersection(nearest1, nearest2, edge[0], edge[1])
            if intersect_point:
                intersect_vec = Vector2D(intersect_point[0], intersect_point[1])
                # pygame.draw.circle(screen, (0,255,0), (int(intersect_point[0]), int(intersect_point[1])),  5)
                # pygame.draw.line(screen, (0,255,0), (int(intersect_vec.x), int(intersect_vec.y)), (int(intersect_vec.x + line_normal.x * 100), int(intersect_vec.y + line_normal.y * 100)), 5)

                # ball.position = intersect_vec - line_normal * (ball.radius + 0.1)
                # ball.velocity = ball.velocity.reflect(line_normal)
                # ball.position += ball.velocity
                return True

        self.color = self.original_color

        for corner in self.corners:
            collision_time = find_circle_collision_time(
                ball.last_position,
                ball.velocity,
                ball.radius,
                corner,
                Vector2D(0, 0),
                0,  # Assuming corner is stationary and has zero radius
            )
            if collision_time and collision_time < 1:
                # Handle the collision (update ball's position and velocity)
                # ball.position = ball.last_position + ball.velocity * (
                #     collision_time - 0.1
                # )
                # collision_normal = (ball.velocity).normalize()
                # ball.velocity = ball.velocity.reflect(
                #     collision_normal
                # ) 
                 # Assuming simple reflection
                return True

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
        pygame.draw.polygon(self.screen, self.color, corners_tuple)


max_damage = 100


class Capsule:
    def __init__(
        self, center, length, thickness=20, angle=0, name="", mirror=False, owner=None, screen=None
    ):
        self.owner = owner
        self.mirror = mirror
        self.center = center
        self.length = length
        self.thickness = thickness
        self.angle = angle
        self.name = name
        self.original_color = (0, 0, 0)
        # Initialize the OBB based on the above properties
        self.obb = OBB(self.center, self.length, self.thickness, self.angle, screen=screen)
        self.damage_taken = 0
        self.time_hit = None

        # Calculate the positions for the balls at each end (centered on the edges)
        delta = Vector2D(
            math.cos(math.radians(angle)), math.sin(math.radians(angle))
        ) * (self.length / 2)
        ball1_pos = self.center - delta
        ball2_pos = self.center + delta

        # Initialize the balls
        self.ball1 = Ball(ball1_pos, thickness / 2, name=f"{name}-ball1", owner=owner, screen=screen)
        self.ball2 = Ball(ball2_pos, thickness / 2, name=f"{name}-ball2", owner=owner, screen=screen)

    @classmethod
    def from_start_end(cls, start_pos, end_pos, radius=20, name="", owner=None, screen=None):
        angle = math.degrees(
            math.atan2(end_pos.y - start_pos.y, end_pos.x - start_pos.x)
        )
        distance = start_pos.distance_to(end_pos)
        center = (start_pos + end_pos) / 2
        length = distance
        return cls(center, length, thickness=radius, angle=angle, name=name, owner=owner, screen=screen)

    @classmethod
    def from_start_angle_distance(
        cls, start_pos, angle, distance, radius=20, name="", mirror=False, owner=None, screen=None
    ):
        end_pos = (
            start_pos
            + Vector2D(math.cos(math.radians(angle)), math.sin(math.radians(angle)))
            * distance
        )
        center = (start_pos + end_pos) / 2
        length = distance
        return cls(center, length, thickness=radius, angle=angle, name=name, owner=owner, screen=screen)

    def update_from_start_angle_distance(self, start_pos, angle, distance):
        end_pos = (
            start_pos
            + Vector2D(math.cos(math.radians(angle)), math.sin(math.radians(angle)))
            * distance
        )
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
        # self.obb.update_corners()

        # Update balls (if they have an update method)
        self.ball1.update()
        self.ball2.update()

    def draw(self):
        if self.damage_taken > 0:
            hit_force_scale = min(self.damage_taken / max_damage, 1)
            current_time = pygame.time.get_ticks()
            delta_time = (current_time - self.time_hit) / (1000)
            ease = 1 - self.owner.easeInQuint(delta_time)
            red = min(255 * hit_force_scale * ease, 255)
            red = max(red, 0)
            self.ball2.color = (red, 0, 0)
            self.ball1.color = (red, 0, 0)
            self.obb.color = (red, 0, 0)
            if ease >= 1:
                self.damage_taken = 0
                self.time_hit = None
        # Draw OBB and balls
        self.ball1.draw()
        self.ball2.draw()
        self.obb.draw()

    def take_damage(self, ball):
        speed = ball.velocity.__abs__()
        self.damage_taken = speed
        self.time_hit = pygame.time.get_ticks()
        # self.ball2.color = (150,0,0)
        # self.ball1.color = (150,0,0)
        # self.obb.color = (150,0,0)
        self.owner.health_bar.take_damage(speed)

    def reset_color(self):
        self.ball2.color = self.original_color
        self.ball1.color = self.original_color
        self.obb.color = self.original_color

    def ball_intersection(self, ball):
        direction = ball.is_moving_away_or_towards(self.owner.body.ball2.position)
        if direction != 1:
            return False

        intersect = self.ball2.ball_intersection(ball)
        if self.name != "body":
            intersect = False
        if intersect:
            self.take_damage(ball)
            return intersect
        intersect = self.obb.ball_intersection(ball)
        if self.name != "body":
            intersect = False
        if intersect:
            self.take_damage(ball)
            return intersect

        self.reset_color()

        return None


class Stickman:
    def __init__(self, x_offset=0, mirror=False, enemy=None, screen = None):
        self.screen = screen
        self.enemy = enemy
        self.mirror = mirror
        self.x_offset = x_offset
        self.glove_state = "idle"  # "idle" or "punching"
        self.glove_velocity = Vector2D(0, 0)
        self.parts = []
        self.move_body_offset = Vector2D(0, 0)

        self.max_health = 1000
        self.player_height = 600
        self.player_width = 100
        self.player_speed = 5
        self.head_radius = 80
        self.half_arm_length = 170
        self.half_leg_length = 230
        self.body_height = 300
        self.feet_length = 50
        self.glove_size = 40
        self.feet_distance = 200
        self.floor_height = 100
        self.feet_left_pos = 100
        self.thickness = 60
        self.glove_color = (150, 0, 0)
        self.punch_distance = 200
        self.punch_speed = 10
        self.SOME_LATENCY_THRESHOLD = 100

        self.body = None
        self.left_leg = None
        self.left_leg2 = None
        self.left_feet = None
        self.right_leg = None
        self.right_leg2 = None
        self.right_feet = None
        self.arm = None
        self.arm2 = None
        self.glove = None
        self.head = None

        self.screen_width = screen.get_width()
        self.init_stick_man(screen=self.screen)
        self.health_bar = HealthBar(self.max_health, Vector2D(300, 100), (255, 0, 0))



    def init_stick_man(self, screen):
        self.screen = screen
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        direction = -1 if self.mirror else 1
        start_pos = Vector2D(self.screen_width / 2 + self.x_offset, self.screen_height - 50)
        self.left_feet = Capsule.from_start_angle_distance(
            start_pos,
            0,
            self.feet_length * direction,
            self.thickness,
            name="left_feet",
            mirror=self.mirror,
            owner=self,
            screen=self.screen
        )
        between_feet = start_pos + Vector2D((self.feet_distance / 2) * direction, 0)
        croutch = between_feet + Vector2D(0, -250 - self.body_height)
        self.body = Capsule(
            croutch,
            self.body_height,
            self.thickness,
            90,
            name="body",
            mirror=self.mirror,
            owner=self,
            screen=self.screen

        )
        self.left_leg = Capsule.from_start_angle_distance(
            self.body.ball2.position,
            90,
            self.half_leg_length,
            self.thickness,
            name="left_leg",
            mirror=self.mirror,
            owner=self,
            screen=self.screen

        )
        self.left_leg2 = Capsule.from_start_angle_distance(
            self.left_leg.ball2.position,
            135,
            self.half_leg_length,
            self.thickness,
            name="left_leg2",
            mirror=self.mirror,
            owner=self,
            screen=self.screen
        )
        self.right_leg = Capsule.from_start_angle_distance(
            self.body.ball2.position,
            0,
            self.half_leg_length,
            self.thickness,
            name="right_leg",
            mirror=self.mirror,
            owner=self,
            screen=self.screen
        )
        self.right_leg2 = Capsule.from_start_angle_distance(
            self.right_leg.ball2.position,
            45,
            self.half_leg_length,
            self.thickness,
            name="right_leg2",
            mirror=self.mirror,
            owner=self,
            screen=self.screen
        )
        self.right_feet = Capsule.from_start_angle_distance(
            self.left_feet.ball2.position + Vector2D(self.feet_distance * direction, 0),
            0,
            self.feet_length * direction,
            self.thickness,
            name="right_feet",
            mirror=self.mirror,
            owner=self,
            screen=self.screen
        )
        self.arm = Capsule.from_start_angle_distance(
            self.body.ball1.position,
            45,
            self.half_arm_length,
            self.thickness,
            name="arm",
            mirror=self.mirror,
            owner=self,
            screen=self.screen
        )
        self.arm2 = Capsule.from_start_angle_distance(
            self.arm.ball2.position,
            -45,
            self.half_arm_length,
            self.thickness,
            name="arm2",
            mirror=self.mirror,
            owner=self,
            screen=self.screen
        )
        self.glove = Ball(
            self.arm2.ball2.position,
            self.glove_size,
            color=self.glove_color,
            name="glove",
            mirror=self.mirror,
            owner=self,
            screen=self.screen
        )
        edge_direction = (
            self.body.obb.edges[0][1] - self.body.obb.edges[0][0]
        ).normalize()
        start = self.body.ball1.position + edge_direction * self.head_radius
        self.head = Ball(
            start, self.head_radius, self.screen, (0, 0, 0), name="head", mirror=self.mirror, owner=self
        )

        self.parts.append(self.body)
        self.parts.append(self.left_leg)
        self.parts.append(self.left_leg2)
        self.parts.append(self.left_feet)
        self.parts.append(self.right_leg)
        self.parts.append(self.right_leg2)
        self.parts.append(self.right_feet)
        self.parts.append(self.arm)
        self.parts.append(self.arm2)
        self.parts.append(self.glove)
        self.parts.append(self.head)

    def draw(self):
        self.body.draw()
        self.left_leg.draw()
        self.left_leg2.draw()
        self.left_feet.draw()
        self.right_leg.draw()
        self.right_leg2.draw()
        self.right_feet.draw()
        self.arm.draw()
        self.arm2.draw()
        self.glove.draw()
        self.head.draw()

    def serialize_positions_and_angles_with_timestamp(self, handshake_time):
        positions_and_angles = {}

        # Calculate the timestamp as the time elapsed since the handshake
        timestamp = pygame.time.get_ticks() - handshake_time

        for part in self.parts:
            if isinstance(part, Ball):
                positions_and_angles[part.name] = {
                    "position": (part.position.x, part.position.y),
                    "type": "Ball",
                }
            elif isinstance(part, Capsule):
                positions_and_angles[part.name] = {
                    "position1": (part.ball1.position.x, part.ball1.position.y),
                    "position2": (part.ball2.position.x, part.ball2.position.y),
                    "angle": part.angle,
                    "type": "Capsule",
                }

        # Include the timestamp in the dictionary
        positions_and_angles["timestamp"] = timestamp

        return json.dumps(positions_and_angles)

    def apply_json_to_player_with_timestamp(self, json_str, handshake_time):
        is_mirrored = True
        positions_and_angles = json.loads(json_str)
        timestamp = positions_and_angles.pop("timestamp", None)

        # Calculate time difference
        time_difference = None
        if timestamp is not None:
            now = pygame.time.get_ticks()
            time_difference = now - (handshake_time + timestamp)

        # Handle latency if needed
        if time_difference and time_difference > self.SOME_LATENCY_THRESHOLD:
            # Interpolation logic here
            pass

        # Assume field_width is the width of the game field
        field_width = self.screen_width

        # Calculate the time difference between the current time and the timestamp in the JSON data
        time_difference = None
        if timestamp is not None:
            now = pygame.time.get_ticks()
            time_difference = now - handshake_time

        for part in self.parts:
            part_info = positions_and_angles.get(part.name, None)
            if part_info is None:
                continue

            if isinstance(part, Ball):
                x, y = part_info["position"]

                # Mirror position if needed
                if is_mirrored:
                    x = field_width - x

                part.position = Vector2D(x, y)
                part.update()

            elif isinstance(part, Capsule):
                x1, y1 = part_info["position1"]
                x2, y2 = part_info["position2"]

                # Mirror positions if needed
                if is_mirrored:
                    x1 = field_width - x1
                    x2 = field_width - x2

                part.update(Vector2D(x1, y1), Vector2D(x2, y2))

        return time_difference

    def serialize(self):
        positions_and_angles = {}

        for part in self.parts:
            # Check if the part is a Ball or a Capsule
            if isinstance(part, Ball):
                positions_and_angles[part.name] = {
                    "position": (part.position.x, part.position.y),
                    "type": "Ball",
                }
            elif isinstance(part, Capsule):
                positions_and_angles[part.name] = {
                    "position1": (part.ball1.position.x, part.ball1.position.y),
                    "position2": (part.ball2.position.x, part.ball2.position.y),
                    "angle": part.angle,
                    "type": "Capsule",
                }

        # Convert the dictionary to a JSON string for serialization
        return json.dumps(positions_and_angles)

    def move_stick_man(self, mouse_position):
        pos_before = self.body.ball2.position
        target = mouse_position + self.move_body_offset
        start_pos1 = self.left_feet.ball1.position
        start_pos2 = self.right_feet.ball1.position
        middle_pos1, end_pos1, middle_pos2, end_pos2 = self.update_positions(
            target,
            start_pos1,
            start_pos2,
            self.half_leg_length,
            self.half_leg_length,
            mirror=self.mirror,
        )

        self.left_leg2.update(start_pos1, middle_pos1)
        self.left_leg.update(middle_pos1, end_pos1)

        self.right_leg2.update(start_pos2, middle_pos2)
        self.right_leg.update(middle_pos2, end_pos2)

        self.body.update_from_start_angle_distance(
            self.left_leg.ball2.position, 90, -self.body_height
        )

        pos_after = self.body.ball2.position
        pos_delta = pos_after - pos_before

        self.arm.update(self.body.ball2.position, self.arm.ball2.position + pos_delta)
        self.arm2.update(self.arm.ball2.position, self.arm2.ball2.position + pos_delta)
        self.glove.position += pos_delta

        # Move the head
        edge_direction = -(
            self.body.obb.edges[0][1] - self.body.obb.edges[0][0]
        ).normalize()
        start = self.body.ball2.position + edge_direction * self.head_radius
        self.head.position = start

    def move_glove_with_mouse(self, mouse_position):
        target = mouse_position
        start = self.body.ball2.position
        middle_pos, end_pos = self.inverse_kinematics(
            start,
            target,
            self.half_arm_length,
            self.half_arm_length,
            mirror=self.mirror,
        )
            # target = target
            # target = self.glove.last_position - self.glove.velocity
            # start = self.body.ball2.position
            # middle_pos, end_pos = inverse_kinematics(start, target, half_arm_length, half_arm_length, mirror=self.mirror)

        self.arm.update(start, middle_pos)
        self.arm2.update(middle_pos, end_pos)

        start = self.arm2.ball2.position
        self.glove.position = start

    def move_punch(self, punch_time, punch_distance=200):
        if self.glove_state == "punching":
            time_scale = self.easeInBack(punch_time)
            if time_scale > 1:
                time_scale = 1
            self.glove.position += self.glove_velocity
            direction = -1 if self.mirror else 1
            final_target = Vector2D(
                self.body.ball2.position.x + (punch_distance + 100) * direction,
                self.body.ball2.position.y,
            )
            start = Vector2D(
                self.body.ball2.position.x + 100 * direction, self.body.ball2.position.y
            )

            target = start + (final_target - start) * time_scale
            if (start - target).__abs__() < 0.0001:
                return
            middle_pos, end_pos = self.inverse_kinematics(
                start,
                target,
                self.half_arm_length,
                self.half_arm_length,
                mirror=self.mirror,
            )
            self.arm.update(start, middle_pos)
            self.arm2.update(middle_pos, end_pos)
            start = self.arm2.ball2.position
            self.glove.position = start
            self.glove.update()
            # self.glove = Ball(start, glove_size, color=glove_color)
            # Stop the punch after reaching a certain distance or another condition
            if self.glove.position.distance_to(final_target) < self.punch_speed * 5:
                start = self.body.ball2.position
                middle_pos, end_pos = self.inverse_kinematics(
                    start,
                    final_target,
                    self.half_arm_length,
                    self.half_arm_length,
                    mirror=self.mirror,
                )
                self.arm.update(start, middle_pos)
                self.arm2.update(middle_pos, end_pos)
                start = self.arm2.ball2.position
                self.glove.position = start
                self.glove.update()
                self.glove_state = "idle"
        elif self.glove_state == "rewind-punch":
            time_scale = self.easeInBack(punch_time)
            self.glove.position += self.glove_velocity

            start = self.glove.position
            final_target = Vector2D(
                self.body.ball2.position.x + 100, self.body.ball2.position.y
            )

            target = start + (final_target - start) * time_scale
            if (start - target).__abs__() < 0.0001:
                return
            middle_pos, end_pos = self.inverse_kinematics(
                start,
                target,
                self.half_arm_length,
                self.half_arm_length,
                mirror=self.mirror,
            )
            self.arm.update(start, middle_pos)
            self.arm2.update(middle_pos, end_pos)
            start = self.arm2.ball2.position
            self.glove.position = start
            self.glove.update()
            # self.glove = Ball(start, glove_size, color=glove_color)
            # Stop the punch after reaching a certain distance or another condition
            if self.glove.position.distance_to(final_target) < self.punch_speed * 5:
                start = self.glove.position
                middle_pos, end_pos = self.inverse_kinematics(
                    start,
                    final_target,
                    self.half_arm_length,
                    self.half_arm_length,
                    mirror=self.mirror,
                )
                self.arm.update(start, middle_pos)
                self.arm2.update(middle_pos, end_pos)
                start = self.arm2.ball2.position
                self.glove.position = start
                self.glove.update()
                self.glove_state = "idle"

    def check_punch_collision(self):
        for part in self.parts:
            intersect = part.ball_intersection(self.enemy.glove)
            if intersect:
                if (self.glove.velocity).__abs__() > 5:
                    self.punch_sound.play()
                return True
        return False

    def inverse_kinematics(self, base_vec, target_vec, l1, l2, mirror=False):
        # Compute the vector from base to target
        base_to_target = target_vec - base_vec

        # Compute the distance from base to target
        distance = abs(base_to_target)

        if distance < 0.0001:
            return base_vec, base_vec
        # Constrain the total reach
        if distance > l1 + l2:
            direction = base_to_target.normalize()
            base_to_target = direction * (l1 + l2)
            target_vec = base_vec + base_to_target
            distance = l1 + l2

        # Two-link arm inverse kinematics formulae
        a1 = math.acos((l1**2 + distance**2 - l2**2) / (2 * l1 * distance))
        if mirror:
            a1 = -a1
        # Get the angle to target
        angle_to_target = math.atan2(base_to_target.y, base_to_target.x)

        # Calculate elbow position
        elbow_direction = Vector2D(
            math.cos(angle_to_target + a1), math.sin(angle_to_target + a1)
        )
        elbow_vec = base_vec + (elbow_direction * l1)

        # Calculate glove position from the elbow
        elbow_to_target = target_vec - elbow_vec
        glove_direction = elbow_to_target.normalize()
        glove_vec = elbow_vec + (glove_direction * l2)

        return elbow_vec, glove_vec

    def update_positions(
        self, mouse_position, base1, base2, l1, l2, threshold=10, mirror=False
    ):
        target = mouse_position
        while True:
            elbow1, glove1 = self.inverse_kinematics(
                base1, target, l1, l2, mirror=mirror
            )
            elbow2, glove2 = self.inverse_kinematics(
                base2, target, l1, l2, mirror=mirror
            )

            delta_glove = glove1 - glove2
            delta_len = delta_glove.__abs__()
            if delta_len < threshold:
                break

            target = glove1 - delta_glove / 2

        # Recalculate the IK for both arms one final time
        new_elbow1, new_glove1 = self.inverse_kinematics(
            base1, target, l1, l2, mirror=mirror
        )
        new_elbow2, new_glove2 = self.inverse_kinematics(
            base2, target, l1, l2, mirror=mirror
        )

        return new_elbow1, new_glove1, new_elbow2, new_glove2

    @staticmethod
    def easeInBack(x):
        c1 = 1.70158
        c3 = c1 + 1

        return c3 * x * x * x - c1 * x * x

    @staticmethod
    def easeInOutSine(x):
        return -(math.cos(math.pi * x) - 1) / 2

    @staticmethod
    def easeInQuint(x):
        return x**5


class StickManGame:
    def __init__(self, init_pygame=True, full_screen=False, screen=None, client_conn=None):
        self.client_conn = client_conn
        # Initialize
        screen_width = 1600
        screen_height = 1200
        self.init_graphics(
            init_pygame, full_screen, screen, screen_width, screen_height
        )

        self.clock = pygame.time.Clock()

        # Initialize two stickmen
        self.stickman1 = Stickman(x_offset=-300, screen=self.screen)
        self.stickman2 = Stickman(x_offset=300, mirror=True, screen=self.screen)
        self.stickman1.enemy=self.stickman2
        self.stickman2.enemy=self.stickman1
        self.move_body_offset = Vector2D(0, 0)
        self.glove_state = "idle"
        self.move_body = False
        self.move_arm = False

        self.stickman1.move_stick_man(self.stickman1.body.ball2.position)
        glove_position = Vector2D(
            self.stickman1.body.ball2.position.x + 100,
            self.stickman1.body.ball2.position.y,
        )
        self.stickman1.move_glove_with_mouse(glove_position)

        self.stickman2.move_stick_man(self.stickman2.body.ball2.position)
        glove_position = Vector2D(
            self.stickman2.body.ball2.position.x - 100,
            self.stickman2.body.ball2.position.y,
        )
        self.stickman2.move_glove_with_mouse(glove_position)

        self.current_time = pygame.time.get_ticks()
        for part in self.stickman1.parts:
            if isinstance(part, Capsule):
                part.ball1.velocity = Vector2D(0, 0)
                part.ball2.velocity = Vector2D(0, 0)
            if hasattr(part, "velocity"):
                part.velocity = Vector2D(0, 0)

        for part in self.stickman2.parts:
            if isinstance(part, Capsule):
                part.ball1.velocity = Vector2D(0, 0)
                part.ball2.velocity = Vector2D(0, 0)
            if hasattr(part, "velocity"):
                part.velocity = Vector2D(0, 0)

        self.mouse_last_pos = Vector2D(0, 0)
        self.controling_stickman = self.stickman1
        self.time_punch_started = 0
        self.punch_sound = pygame.mixer.Sound(f"{base_path}\\assets\\\sounds\\sfx-punch2.mp3")

        # Create a queue to hold received data
        self.data_queue = queue.Queue()

    def init_graphics(self, init_pygame, full_screen, screen, width, height):
        self.init_pygame = init_pygame
        if init_pygame:
            pygame.init()
            self.full_screen = full_screen

            # Setup screen
            info = pygame.display.Info()
            if self.full_screen:
                self.screen_width = info.current_w
                self.screen_height = info.current_h
                self.screen = pygame.display.set_mode(
                    (self.screen_width, self.screen_height), pygame.FULLSCREEN
                )
            else:
                self.screen_width = width
                self.screen_height = height
                self.screen = pygame.display.set_mode(
                    (self.screen_width, self.screen_height)
                )
        else:
            self.screen_width = width
            self.screen_height = height
            self.screen = pygame.display.set_mode(
                (self.screen_width, self.screen_height)
            )

    def receive_data_thread(self, client_conn, data_queue):
        while True:
            if self.client_conn is None:
                break
            data = self.client_conn.receive_data()
            data_queue.put(data)

    def run(self):
        # Create and start the receiving thread
        #client_conn = Connection(host="127.0.0.1", port=65432)
        #client_conn.flush_buffer()
        #client_conn.perform_handshake(is_server=False)
        handshake_time = pygame.time.get_ticks()
        recv_thread = threading.Thread(
            target=self.receive_data_thread, args=(self.client_conn, self.data_queue)
        )
        recv_thread.start()

        self.player2_connected = False

        while True:
            # Non-blocking check for new data
            try:
                player2_json = self.data_queue.get_nowait()
                self.stickman2.apply_json_to_player_with_timestamp(
                    player2_json, handshake_time
                )
                # Process data
            except queue.Empty:
                pass

            self.screen.fill((200, 200, 200))
            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                # Handle mouse and keyboard events for stickmen here
                pass

                # Check for right mouse button press
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pressed = pygame.mouse.get_pressed()
                    if mouse_pressed[2]:
                        self.move_body = True
                        self.controling_stickman.move_body_offset = (
                            self.controling_stickman.body.ball1.position
                            - Vector2D(
                                pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]
                            )
                        )
                    elif mouse_pressed[0]:
                        self.move_arm = True
                    elif mouse_pressed[1]:
                        if self.controling_stickman.glove_state == "idle":
                            self.controling_stickman.glove_state = "punching"
                            # Set velocity and direction for the punch
                            glove_velocity = Vector2D(
                                10, 0
                            )  # Replace with your desired velocity and direction
                            self.time_punch_started = pygame.time.get_ticks()

                # Check for right mouse button release
                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 3:
                        self.move_body = False
                    elif event.button == 1:
                        self.move_arm = False
                    elif event.button == 2:
                        self.controling_stickman.glove_state = "rewind-punch"
                        # Set velocity and direction for the punch
                        glove_velocity = Vector2D(
                            10, 0
                        )  # Replace with your desired velocity and direction
                        self.time_punch_started = pygame.time.get_ticks()

            # punch_time = (current_time - time_punch_started) / (1000 / punch_speed)
            # controling_stickman.move_punch(punch_time, punch_distance)

            # controling_stickman.move_punch(punch_time, punch_distance)
            mouse_position = Vector2D(
                pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]
            )
            if self.move_arm:
                self.controling_stickman.move_glove_with_mouse(mouse_position)

            if self.move_body:
                self.controling_stickman.move_stick_man(mouse_position)

            self.controling_stickman.glove.update()

            if self.stickman2.check_punch_collision():
                if self.move_arm:
                    self.controling_stickman.move_glove_with_mouse(self.controling_stickman.glove.position)


            self.controling_stickman.draw()

            self.stickman1.health_bar.update(self.screen)
            self.stickman1.health_bar.draw(self.screen)
            self.stickman2.health_bar.update(self.screen)
            self.stickman2.health_bar.draw(self.screen)

            self.stickman2.draw()
            self.controling_stickman.glove.last_position = self.controling_stickman.glove.position
            

            self.mouse_last_pos = mouse_position
            pygame.display.update()
            if self.client_conn is not None:
                self.client_conn.send_command("client_data", "system", 
                    self.controling_stickman.serialize_positions_and_angles_with_timestamp(
                        handshake_time
                    )
                )
            self.clock.tick(60)


game = StickManGame()
game.run()