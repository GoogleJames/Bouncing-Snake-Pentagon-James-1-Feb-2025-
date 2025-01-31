import pygame
import math
import sys

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bouncing Snake in Rotating Pentagon")
clock = pygame.time.Clock()

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Pentagon properties
CENTER = (WIDTH//2, HEIGHT//2)
RADIUS = 250
NUM_SIDES = 5
ROTATION_SPEED = 0.5  # Degrees per frame

# Snake properties
SNAKE_SPEED = 3
TAIL_LENGTH = 50
SNAKE_SIZE = 8

class Pentagon:
    def __init__(self):
        self.angle = 0
        self.vertices = []
        self.edges = []
        self.update_vertices()
        
    def update_vertices(self):
        self.vertices = []
        angle_step = 360 / NUM_SIDES
        current_angle = self.angle
        for _ in range(NUM_SIDES):
            x = CENTER[0] + RADIUS * math.cos(math.radians(current_angle))
            y = CENTER[1] + RADIUS * math.sin(math.radians(current_angle))
            self.vertices.append((x, y))
            current_angle += angle_step
        
        # Create edges as (start, end, normal)
        self.edges = []
        for i in range(NUM_SIDES):
            start = self.vertices[i]
            end = self.vertices[(i+1)%NUM_SIDES]
            # Calculate edge normal (pointing inward)
            edge = (end[0] - start[0], end[1] - start[1])
            normal = (-edge[1], edge[0])
            length = math.hypot(normal[0], normal[1])
            if length == 0:
                length = 1
            normal = (normal[0]/length, normal[1]/length)
            self.edges.append((start, end, normal))
        
    def rotate(self):
        self.angle = (self.angle + ROTATION_SPEED) % 360
        self.update_vertices()
        
    def draw(self, surface):
        pygame.draw.polygon(surface, WHITE, self.vertices, 2)

class Snake:
    def __init__(self):
        self.position = list(CENTER)
        self.direction = [1, 0]  # Initial direction
        self.tail = [tuple(self.position)] * TAIL_LENGTH
        self.speed = SNAKE_SPEED
        
    def update(self, pentagon):
        # Update position
        self.position[0] += self.direction[0] * self.speed
        self.position[1] += self.direction[1] * self.speed
        
        # Check collisions with pentagon edges
        for edge in pentagon.edges:
            start, end, normal = edge
            # Vector from edge start to snake position
            rel_pos = (self.position[0] - start[0], self.position[1] - start[1])
            # Dot product with normal
            dot = rel_pos[0] * normal[0] + rel_pos[1] * normal[1]
            
            if dot < 0:  # Outside the edge
                # Reflect direction
                reflect = [self.direction[0], self.direction[1]]
                dn = 2 * (reflect[0] * normal[0] + reflect[1] * normal[1])
                reflect[0] -= dn * normal[0]
                reflect[1] -= dn * normal[1]
                # Normalize direction
                length = math.hypot(reflect[0], reflect[1])
                if length > 0:
                    self.direction = [reflect[0]/length, reflect[1]/length]
                # Move back inside
                self.position[0] += normal[0] * (-dot + 1)
                self.position[1] += normal[1] * (-dot + 1)
                break
        
        # Update tail
        self.tail.pop()
        self.tail.insert(0, tuple(self.position))
        
    def draw(self, surface):
        # Draw tail
        for i, pos in enumerate(self.tail):
            alpha = 255 * (1 - i/TAIL_LENGTH)
            color = (0, 255, 0, alpha)
            radius = SNAKE_SIZE * (1 - i/(TAIL_LENGTH*2))
            pygame.draw.circle(surface, GREEN, (int(pos[0]), int(pos[1])), int(radius))
        # Draw head
        pygame.draw.circle(surface, RED, (int(self.position[0]), int(self.position[1])), SNAKE_SIZE)

def main():
    pentagon = Pentagon()
    snake = Snake()
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
        screen.fill(BLACK)
        
        # Update and draw objects
        pentagon.rotate()
        pentagon.draw(screen)
        snake.update(pentagon)
        snake.draw(screen)
        
        pygame.display.flip()
        clock.tick(60)
        
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()