from math import isclose
from typing import List, Union
from Vector2D import Vector2D
import math


def distanceSegmentToPoint(A, B, C):
    # Compute vectors AC and AB
    AC = C - A
    AB = B - A

    # Get point D by taking the projection of AC onto AB then adding the offset of A
    D = AC.proj(AB) + A

    AD = D - A
    # D might not be on AB so calculate k of D down AB (aka solve AD = k * AB)
    # We can use either component, but choose larger value to reduce the chance of dividing     
    k = AD.x / AB.x if abs(AB.x) > abs(AB.y) else AD.y / AB.y

    # Check if D is off either end of the line segment
    if k <= 0.0:
        return math.sqrt(C.hypot2(A))
    elif k >= 1.0:
        return math.sqrt(C.hypot2(B))

    return math.sqrt(C.hypot2(D))

def line_circle_nearest_point(A, B, circle_pos, radius):
    AB = B - A
    perp = AB.perpendicular()
    line_normal = perp.normalize()
    nearest_point = circle_pos + line_normal * radius
    line_normal = line_normal.normalize()
    return nearest_point, line_normal

def edge_intersection(p1: Vector2D, p2: Vector2D, p3: Vector2D, p4: Vector2D) -> list:
    d1 = p2 - p1
    d2 = p4 - p3

    den = (d2.y * d1.x - d2.x * d1.y)

    if den == 0:
        return []

    ua = (d2.x * (p1.y - p3.y) - d2.y * (p1.x - p3.x)) / (den + 1e-16)
    ub = (d1.x * (p1.y - p3.y) - d1.y * (p1.x - p3.x)) / (den + 1e-16)

    if ua < 0 or ua > 1 or ub < 0 or ub > 1:
        return []

    intersection = p1 + ua * d1
    return [intersection.x, intersection.y]

# def circle_line_intersection(circle_center, radius, line_point1, line_point2):
#     a, b = circle_center.x, circle_center.y
#     x1, y1 = line_point1.x, line_point1.y
#     x2, y2 = line_point2.x, line_point2.y

#     # Compute the slope (m) and y-intercept (c) of the line
#     m = (y2 - y1) / (x2 - x1)
#     c = y1 - m * x1

#     aprim = 1 + m ** 2
#     bprim = 2 * m * (c - b) - 2 * a
#     cprim = a ** 2 + (c - b) ** 2 - radius ** 2

#     delta = bprim ** 2 - 4 * aprim * cprim

#     # If delta is negative, no intersection
#     if delta < 0:
#         return []

#     x1_e_intersection = (-bprim + math.sqrt(delta)) / (2 * aprim)
#     y1_e_intersection = m * x1_e_intersection + c

#     x2_e_intersection = (-bprim - math.sqrt(delta)) / (2 * aprim)
#     y2_e_intersection = m * x2_e_intersection + c

#     intersection1 = Vector2D(x1_e_intersection, y1_e_intersection)
#     intersection2 = Vector2D(x2_e_intersection, y2_e_intersection)

#     return [intersection1, intersection2]

def circle_line_intersection(circle_center: Vector2D, circle_radius: float,
                             line_point: Vector2D, line_direction: Vector2D) -> List[Vector2D]:
    # Calculate the coefficients of the quadratic equation
    a = line_direction.x**2 + line_direction.y**2
    b = 2 * (line_direction.x * (line_point.x - circle_center.x) + line_direction.y * (line_point.y - circle_center.y))
    c = (line_point.x - circle_center.x)**2 + (line_point.y - circle_center.y)**2 - circle_radius**2

    # Calculate the discriminant
    discriminant = b**2 - 4 * a * c

    # Check the number of intersection points
    if discriminant < 0:
        # No intersection points
        return []
    elif discriminant == 0:
        # Tangent, one intersection point
        t = -b / (2 * a)
        intersection = Vector2D(line_point.x + t * line_direction.x, line_point.y + t * line_direction.y)
        return [intersection]
    else:
        # Two intersection points
        t1 = (-b + math.sqrt(discriminant)) / (2 * a)
        t2 = (-b - math.sqrt(discriminant)) / (2 * a)
        intersection1 = Vector2D(line_point.x + t1 * line_direction.x, line_point.y + t1 * line_direction.y)
        intersection2 = Vector2D(line_point.x + t2 * line_direction.x, line_point.y + t2 * line_direction.y)
        return [intersection1, intersection2]
    
def find_circle_collision_time(p1, v1, r1, p2, v2, r2):
    # Relative position and velocity
    dp = p2 - p1
    dv = v2 - v1

    A = dv.dot(dv)
    B = 2 * dp.dot(dv)
    C = dp.dot(dp) - (r1 + r2) ** 2

    # Quadratic formula to find time
    discriminant = B ** 2 - 4 * A * C

    if discriminant < 0:
        return None  # No collision
    
    t1 = (-B + discriminant ** 0.5) / (2 * A)
    t2 = (-B - discriminant ** 0.5) / (2 * A)

    # Return the smallest positive time
    if t1 > 0 and t2 > 0:
        return min(t1, t2)
    elif t1 > 0:
        return t1
    elif t2 > 0:
        return t2
    else:
        return None  # No future collision    
    
def find_circle_collision_time(p1, v1, r1, p2, v2, r2):
    # # Check if both velocities are zero
    # if v1.__abs__() <= 0.0001 and v2.__abs__() <= 0.0001:
    #     # Circles are stationary, so just check their current positions
    #     if (p1 - p2).__abs__() <= (r1 + r2):
    #         return 1  # Colliding at t=0
    #     else:
    #         return None  # Not colliding    
    # Calculate A, B and C for the quadratic equation
    A = (v1 - v2).dot(v1 - v2)
    B = 2 * (v1 - v2).dot(p1 - p2)
    C = (p1 - p2).dot(p1 - p2) - (r1 + r2)**2

    # Solve the quadratic equation
    discriminant = B**2 - 4*A*C

    if discriminant < 0:
        return None  # No real roots, no collision

    sqrt_discriminant = discriminant ** 0.5
    t1 = (-B + sqrt_discriminant) / (2 * A)
    t2 = (-B - sqrt_discriminant) / (2 * A)

    # We're interested in the smallest positive t, as that would be the first collision point
    if t1 >= 0 and t2 >= 0:
        return min(t1, t2)
    elif t1 >= 0:
        return t1
    elif t2 >= 0:
        return t2
    else:
        return None  # Both times are negative, no future collision

