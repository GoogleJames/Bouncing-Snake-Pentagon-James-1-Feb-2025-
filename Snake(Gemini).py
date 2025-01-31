import pygame
import math

# Initialize Pygame
pygame.init()

# Screen dimensions
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Bouncing Snake Pentagon")

# Colors
white = (255, 255, 255)
black = (0, 0, 0)
green = (0, 255, 0)
red = (255, 0, 0)

# Pentagon parameters
pentagon_center = [screen_width // 2, screen_height // 2]
pentagon_radius = 200
pentagon_rotation_speed = 0.01  # Radians per frame
pentagon_rotation_angle = 0

def get_pentagon_vertices(center, radius, angle):
    vertices = []
    for i in range(5):
        angle_radians = math.radians(72 * i) + angle
        x = center[0] + radius * math.cos(angle_radians)
        y = center[1] + radius * math.sin(angle_radians)
        vertices.append([x, y])
    return vertices

def draw_pentagon(vertices):
    pygame.draw.polygon(screen, white, vertices, 2)

# Snake parameters
snake_length = 20
snake_segment_radius = 8
snake_segments = []
snake_head_pos = [screen_width // 2 - 100, screen_height // 2 - 100]  # Initial position
snake_segments.append(list(snake_head_pos)) # Add head
for _ in range(snake_length - 1): # Add body segments
    snake_segments.append(list(snake_head_pos))  # Initialize body at same pos for now
snake_speed = 3
snake_direction = [1, 1] # Initial direction (x, y)


def draw_snake(segments):
    for i in range(len(segments)):
        pygame.draw.circle(screen, green, (int(segments[i][0]), int(segments[i][1])), snake_segment_radius)
        if i > 0: # Draw connecting lines between segments
            pygame.draw.line(screen, green, (int(segments[i-1][0]), int(segments[i-1][1])), (int(segments[i][0]), int(segments[i][1])), snake_segment_radius * 2 // 3)


def normalize_vector(vec):
    magnitude = math.sqrt(vec[0]**2 + vec[1]**2)
    if magnitude == 0:
        return [0, 0]
    return [vec[0] / magnitude, vec[1] / magnitude]

def reflect_vector(velocity, edge_normal):
    # Reflect velocity vector across the edge normal
    dot_product = velocity[0] * edge_normal[0] + velocity[1] * edge_normal[1]
    reflected_x = velocity[0] - 2 * dot_product * edge_normal[0]
    reflected_y = velocity[1] - 2 * dot_product * edge_normal[1]
    return [reflected_x, reflected_y]


def check_collision_pentagon(snake_head, pentagon_vertices):
    for i in range(5):
        p1 = pentagon_vertices[i]
        p2 = pentagon_vertices[(i + 1) % 5] # Next vertex, wrap around

        edge_vector = [p2[0] - p1[0], p2[1] - p1[1]]
        edge_normal = [-edge_vector[1], edge_vector[0]] # 90 degree rotation for normal
        edge_normal = normalize_vector(edge_normal)

        segment_vector = [snake_head[0] - p1[0], snake_head[1] - p1[1]]

        # Project snake_head onto the normal of the edge
        projection = segment_vector[0] * edge_normal[0] + segment_vector[1] * edge_normal[1]

        # Project snake_head onto the edge vector
        edge_projection = segment_vector[0] * normalize_vector(edge_vector)[0] + segment_vector[1] * normalize_vector(edge_vector)[1]


        # Check if the projection is "inside" the edge bounds (not past endpoints)
        edge_length_sq = (p2[0] - p1[0])**2 + (p2[1] - p1[1])**2
        edge_proj_ratio = edge_projection / math.sqrt(edge_length_sq)


        if 0 <= edge_proj_ratio <= 1 and projection < snake_segment_radius:  # Collision detected! projection < radius
            return edge_normal
    return None # No collision

# Game loop
running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Clear screen
    screen.fill(black)

    # Rotate pentagon
    pentagon_rotation_angle += pentagon_rotation_speed
    pentagon_vertices = get_pentagon_vertices(pentagon_center, pentagon_radius, pentagon_rotation_angle)
    draw_pentagon(pentagon_vertices)

    # Move snake head
    snake_head_pos[0] += snake_direction[0] * snake_speed
    snake_head_pos[1] += snake_direction[1] * snake_speed
    snake_segments[0] = list(snake_head_pos) # Update head segment position

    # Collision detection with pentagon for snake head
    collision_normal = check_collision_pentagon(snake_head_pos, pentagon_vertices)
    if collision_normal:
        snake_direction = reflect_vector(snake_direction, collision_normal)
        # Adjust snake position slightly to avoid sticking inside after reflection (optional)
        snake_head_pos[0] += collision_normal[0] * 1.1 * snake_segment_radius # push a bit along normal
        snake_head_pos[1] += collision_normal[1] * 1.1 * snake_segment_radius


    # Snake body follows head (simple follow mechanism)
    for i in range(1, snake_length):
        segment_diff_x = snake_segments[i-1][0] - snake_segments[i][0]
        segment_diff_y = snake_segments[i-1][1] - snake_segments[i][1]
        snake_segments[i][0] += segment_diff_x * 0.3  # Adjust 0.3 for follow speed
        snake_segments[i][1] += segment_diff_y * 0.3


    # Keep snake within screen bounds (optional, pentagon should contain it in this setup)
    # if snake_head_pos[0] < 0 or snake_head_pos[0] > screen_width or snake_head_pos[1] < 0 or snake_head_pos[1] > screen_height:
    #     snake_direction = reflect_vector(snake_direction, [1 if snake_head_pos[0] < 0 or snake_head_pos[0] > screen_width else 0,
    #                                                     1 if snake_head_pos[1] < 0 or snake_head_pos[1] > screen_height else 0])


    # Draw snake
    draw_snake(snake_segments)


    # Update display
    pygame.display.flip()

    # Control frame rate
    clock.tick(60) # 60 FPS

pygame.quit()