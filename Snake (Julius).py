# Import necessary libraries
import pygame
import math
import sys

# Initialize pygame
pygame.init()

# Setup the screen
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Bouncing Snake in a Rotating Pentagon')

# Clock to control the frame rate
clock = pygame.time.Clock()

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Define pentagon parameters
pentagon_center = (width//2, height//2)
pentagon_radius = 250
num_sides = 5

# Function to calculate the vertices of a regular pentagon given center, radius and rotation angle
def get_pentagon_vertices(center, radius, rotation_angle):
    cx, cy = center
    vertices = []
    for i in range(num_sides):
        angle = math.radians(360/num_sides * i) + rotation_angle
        x = cx + radius * math.cos(angle)
        y = cy + radius * math.sin(angle)
        vertices.append((x, y))
    return vertices

# Snake properties
snake_length = 100  # number of segments
snake_points = []
# Start snake in center with a given initial direction
head = [width//2, height//2]
snake_points.append(head[:])
snake_dir = [3, 2]  # velocity vector

# To keep a tail for the snake history, we store recent positions
max_points = snake_length

# Rotation of the pentagon
rotation = 0
rotation_speed = 0.005  # radians per frame

# Collision detection helper functions
# Function to get line from two points (for collision) if segment intersects with any edge of pentagon

def line_intersection(p0, p1, p2, p3):
    # returns a tuple (bool, point)
    s10_x = p1[0] - p0[0]
    s10_y = p1[1] - p0[1]
    s32_x = p3[0] - p2[0]
    s32_y = p3[1] - p2[1]

    denom = s10_x * s32_y - s32_x * s10_y
    if denom == 0:
        return (False, (0, 0))  # Collinear or parallel

    denom_positive = denom > 0

    s02_x = p0[0] - p2[0]
    s02_y = p0[1] - p2[1]

    s_numer = s10_x * s02_y - s10_y * s02_x
    if (s_numer < 0) == denom_positive:
        return (False, (0, 0))

    t_numer = s32_x * s02_y - s32_y * s02_x
    if (t_numer < 0) == denom_positive:
        return (False, (0, 0))

    if (s_numer > denom) == denom_positive or (t_numer > denom) == denom_positive:
        return (False, (0, 0))

    # Collision detected
    t = t_numer / denom
    intersection_point = (p0[0] + (t * s10_x), p0[1] + (t * s10_y))
    return (True, intersection_point)

# Function to reflect the velocity vector across a line defined by two points (edge of pentagon)

def reflect_velocity(vel, edge_start, edge_end):
    # edge vector
    edge_vec = (edge_end[0]-edge_start[0], edge_end[1]-edge_start[1])
    # normalize edge vector
    edge_length = math.hypot(edge_vec[0], edge_vec[1])
    if edge_length == 0:
        return vel
    edge_unit = (edge_vec[0]/edge_length, edge_vec[1]/edge_length)

    # normal to the edge (rotate by 90 degrees)
    normal = (-edge_unit[1], edge_unit[0])
    # reflect velocity v across normal: v' = v - 2*(v dot n)*n
    v_dot_n = vel[0]*normal[0] + vel[1]*normal[1]
    new_vel = (vel[0] - 2*v_dot_n*normal[0], vel[1] - 2*v_dot_n*normal[1])
    return new_vel

# Main loop
running = True
while running:
    dt = clock.tick(60)  # 60 FPS
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update pentagon rotation
    rotation += rotation_speed

    # Get current pentagon vertices for collision detection and drawing
    pentagon_vertices = get_pentagon_vertices(pentagon_center, pentagon_radius, rotation)

    # Update snake head position
    head[0] += snake_dir[0]
    head[1] += snake_dir[1]

    # Check collision with pentagon edges
    collision_detected = False

    # iterate through each edge of pentagon
    for i in range(len(pentagon_vertices)):
        p1 = pentagon_vertices[i]
        p2 = pentagon_vertices[(i + 1) % len(pentagon_vertices)]
        collided, pt = line_intersection(snake_points[-1], head, p1, p2)
        if collided:
            collision_detected = True
            # Reflect the snake_dir with respect to the edge
            snake_dir = list(reflect_velocity(snake_dir, p1, p2))
            # Move head back to collision point to avoid sticking
            head[0], head[1] = pt
            break

    # Append new head position to snake_points
    snake_points.append(head[:])

    # Keep only max_points
    if len(snake_points) > max_points:
        snake_points.pop(0)

    # Clear screen
    screen.fill(BLACK)

    # Draw the rotating pentagon
    pygame.draw.polygon(screen, BLUE, pentagon_vertices, 3)

    # Draw the snake
    if len(snake_points) > 1:
        pygame.draw.lines(screen, GREEN, False, snake_points, 3)
        # Draw head as red circle
        pygame.draw.circle(screen, RED, (int(head[0]), int(head[1])), 5)

    pygame.display.flip()

pygame.quit()
sys.exit()

print('Script executed successfully')