import pygame
import math
import numpy as np

# Initialize Pygame
pygame.init()

# Set up the display
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bouncing Snake in Rotating Pentagon")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)

class Snake:
    def __init__(self, x, y):
        self.segments = [(x, y)]
        self.length = 20  # Number of segments
        self.spacing = 10  # Space between segments
        self.velocity = [4, 4]  # Initial velocity
        
        # Initialize snake segments
        for i in range(1, self.length):
            self.segments.append((x - i * self.spacing, y))
    
    def update(self):
        # Update head position
        new_x = self.segments[0][0] + self.velocity[0]
        new_y = self.segments[0][1] + self.velocity[1]
        self.segments.insert(0, (new_x, new_y))
        self.segments.pop()
    
    def draw(self, screen):
        for i, segment in enumerate(self.segments):
            # Gradient color from head to tail
            color_val = 255 - (i * 155 // self.length)
            color = (0, color_val, 0)
            pygame.draw.circle(screen, color, (int(segment[0]), int(segment[1])), 5)

class Pentagon:
    def __init__(self, center_x, center_y, radius):
        self.center_x = center_x
        self.center_y = center_y
        self.radius = radius
        self.rotation = 0
        self.rotation_speed = 0.5  # Degrees per frame
        
    def get_vertices(self):
        vertices = []
        for i in range(5):
            angle = math.radians(self.rotation + i * 72)  # 72 degrees = 360/5
            x = self.center_x + self.radius * math.cos(angle)
            y = self.center_y + self.radius * math.sin(angle)
            vertices.append((x, y))
        return vertices
    
    def draw(self, screen):
        vertices = self.get_vertices()
        pygame.draw.polygon(screen, WHITE, vertices, 2)
    
    def rotate(self):
        self.rotation += self.rotation_speed

def get_line_intersection(p1, p2, p3, p4):
    """Calculate intersection point of two line segments"""
    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = p3
    x4, y4 = p4
    
    denominator = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if denominator == 0:
        return None
    
    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denominator
    
    if 0 <= t <= 1:
        x = x1 + t * (x2 - x1)
        y = y1 + t * (y2 - y1)
        return (x, y)
    return None

def check_collision(snake, pentagon):
    """Check collision between snake head and pentagon walls"""
    vertices = pentagon.get_vertices()
    head = snake.segments[0]
    next_head = (head[0] + snake.velocity[0], head[1] + snake.velocity[1])
    
    for i in range(5):
        v1 = vertices[i]
        v2 = vertices[(i + 1) % 5]
        
        intersection = get_line_intersection(head, next_head, v1, v2)
        if intersection:
            # Calculate normal vector of the wall
            wall_vector = (v2[0] - v1[0], v2[1] - v1[1])
            wall_normal = (-wall_vector[1], wall_vector[0])
            normal_length = math.sqrt(wall_normal[0]**2 + wall_normal[1]**2)
            wall_normal = (wall_normal[0]/normal_length, wall_normal[1]/normal_length)
            
            # Reflect velocity vector
            dot_product = (snake.velocity[0] * wall_normal[0] + 
                         snake.velocity[1] * wall_normal[1])
            snake.velocity[0] = snake.velocity[0] - 2 * dot_product * wall_normal[0]
            snake.velocity[1] = snake.velocity[1] - 2 * dot_product * wall_normal[1]
            return True
    return False

# Create game objects
snake = Snake(WIDTH//2, HEIGHT//2)
pentagon = Pentagon(WIDTH//2, HEIGHT//2, 200)

# Game loop
running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # Update
    check_collision(snake, pentagon)
    snake.update()
    pentagon.rotate()
    
    # Draw
    screen.fill(BLACK)
    pentagon.draw(screen)
    snake.draw(screen)
    
    # Update display
    pygame.display.flip()
    clock.tick(60)

pygame.quit()