import pygame
import math

#########################
#  CONFIGURATION
#########################
WINDOW_WIDTH  = 800
WINDOW_HEIGHT = 600
FPS = 60

# Pentagon / snake settings
PENTAGON_RADIUS = 200
PENTAGON_SIDES  = 5
ROTATION_SPEED  = 0.01  # Radians per frame
SNAKE_SPEED     = 3.0
SNAKE_HEAD_RADIUS = 10
SNAKE_LENGTH    = 30  # number of segments in snake
SNAKE_SEGMENT_SPACING = 4  # distance between consecutive snake segments

#########################
#  INITIALIZE PYGAME
#########################
pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Rotating Pentagon Bouncing Snake")
clock = pygame.time.Clock()

#########################
#  HELPER FUNCTIONS
#########################

def create_pentagon_points(center, radius, sides=5, rotation=0.0):
    """
    Return a list of (x, y) points for a regular polygon (pentagon by default)
    given:
      - center (cx, cy)
      - radius
      - sides (default=5)
      - rotation offset in radians
    """
    cx, cy = center
    points = []
    for i in range(sides):
        angle = 2.0 * math.pi * i / sides + rotation
        x = cx + radius * math.cos(angle)
        y = cy + radius * math.sin(angle)
        points.append((x, y))
    return points

def point_in_polygon(pt, polygon):
    """
    Determine if point pt=(x,y) is inside a polygon using the ray-casting method.
    Returns True if inside, False if outside.
    """
    x, y = pt
    inside = False
    n = len(polygon)
    for i in range(n):
        x1, y1 = polygon[i]
        x2, y2 = polygon[(i+1) % n]
        # Check if the line from (x1,y1)->(x2,y2) intersects with
        # a ray going to the right from point (x,y).
        if ((y1 > y) != (y2 > y)):
            # Compute the x-coordinate where it intersects
            intersectX = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
            if intersectX > x:  # a valid crossing
                inside = not inside
    return inside

def distance_point_to_line_segment(px, py, x1, y1, x2, y2):
    """
    Returns the distance from point (px,py) to the line segment from (x1,y1) to (x2,y2).
    Also returns the normal vector (nx, ny) from the segment to the point
    (unnormalized, but pointing outward from the polygon side).
    """
    # Line segment vector
    seg_vx = x2 - x1
    seg_vy = y2 - y1

    # Vector from (x1,y1) to our point (px,py)
    pt_vx = px - x1
    pt_vy = py - y1

    seg_len_sq = seg_vx**2 + seg_vy**2
    # Project pt_v onto seg_v to find the parameter t of the projection
    if seg_len_sq > 1e-8:
        t = (pt_vx * seg_vx + pt_vy * seg_vy) / seg_len_sq
    else:
        t = 0.0

    # Clamp t to [0,1] so we get the nearest point on the *segment*
    t = max(0.0, min(1.0, t))

    # Find the closest point on the line segment
    closest_x = x1 + t * seg_vx
    closest_y = y1 + t * seg_vy

    # Vector from (closest_x, closest_y) to (px, py)
    dx = px - closest_x
    dy = py - closest_y
    dist = math.hypot(dx, dy)

    # Normal vector from line to point (points outward from the segment)
    # If the polygon is defined in CCW order, we can define outward based on left normal
    # but for simplicity, we just compute a direct vector from the line to the point.
    # We'll normalize it only if needed for reflection calculations.
    return dist, (dx, dy)


def reflect_velocity(vel, normal):
    """
    Reflect velocity vector vel=(vx,vy) around the normal vector normal=(nx,ny).
    Normal should ideally be normalized. If not, we normalize it here.
    Reflection formula: v' = v - 2*(v·n)*n
    """
    vx, vy = vel
    nx, ny = normal
    # normalize n
    mag_n = math.hypot(nx, ny)
    if mag_n < 1e-8:
        return vel  # can't reflect around a zero vector
    nx /= mag_n
    ny /= mag_n
    # dot product
    dot = vx*nx + vy*ny
    # reflection
    rx = vx - 2*dot*nx
    ry = vy - 2*dot*ny
    return (rx, ry)

#########################
#  MAIN LOOP SETUP
#########################

# Center of screen
center_x = WINDOW_WIDTH // 2
center_y = WINDOW_HEIGHT // 2

# Snake will be stored as a list of (x,y) from head to tail
snake_positions = []
snake_positions.append((center_x, center_y))  # start with just a head
# We can fill initial positions behind head:
for i in range(1, SNAKE_LENGTH):
    snake_positions.append((center_x - i*SNAKE_SEGMENT_SPACING, center_y))

# Snake velocity (head). Start moving diagonally
snake_velocity = (SNAKE_SPEED, -SNAKE_SPEED)

# Keep track of rotation angle for the pentagon
pentagon_angle = 0.0

running = True

while running:
    dt = clock.tick(FPS) / 1000.0  # seconds passed since last frame
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update pentagon rotation
    pentagon_angle += ROTATION_SPEED

    # 1) Update snake head position
    head_x, head_y = snake_positions[0]
    vx, vy = snake_velocity

    new_head_x = head_x + vx
    new_head_y = head_y + vy

    # 2) Build the new pentagon (rotated)
    pentagon_points = create_pentagon_points(
        (center_x, center_y),
        PENTAGON_RADIUS,
        sides=PENTAGON_SIDES,
        rotation=pentagon_angle
    )

    # 3) Check collision:
    #    We'll see if the new head position is *outside* the pentagon.
    #    If it is outside, we attempt a more accurate reflection using the nearest edge.
    if not point_in_polygon((new_head_x, new_head_y), pentagon_points):
        # Attempt to reflect around the nearest pentagon edge
        # Find the edge that gives the minimal distance to head
        min_dist = float('inf')
        best_normal = (0, 0)

        for i in range(len(pentagon_points)):
            x1, y1 = pentagon_points[i]
            x2, y2 = pentagon_points[(i+1) % len(pentagon_points)]
            dist, normal_vec = distance_point_to_line_segment(
                new_head_x, new_head_y, x1, y1, x2, y2
            )
            if dist < min_dist:
                min_dist = dist
                best_normal = normal_vec

        # Reflect velocity
        snake_velocity = reflect_velocity(snake_velocity, best_normal)

        # Recompute new head after reflection
        vx, vy = snake_velocity
        new_head_x = head_x + vx
        new_head_y = head_y + vy

        # Optional: you could clamp the head slightly inside so it doesn't get stuck outside
        # This naive approach simply repositions the head a bit:
        # new_head_x = head_x + vx * 0.5
        # new_head_y = head_y + vy * 0.5

    # 4) Update snake body:
    #    Move the head to new position and "pull" each segment after it
    snake_positions.insert(0, (new_head_x, new_head_y))  # new head at front
    snake_positions.pop()  # remove last tail segment to keep length

    # 5) RENDER
    screen.fill((0, 0, 0))

    # Draw pentagon
    pygame.draw.polygon(screen, (255, 255, 255), pentagon_points, width=2)

    # Draw snake (simple approach: draw circles for each segment)
    for i, pos in enumerate(snake_positions):
        color = (200, 200, 50) if i == 0 else (0, 255, 0)
        pygame.draw.circle(screen, color, (int(pos[0]), int(pos[1])), SNAKE_HEAD_RADIUS)

    # Show everything
    pygame.display.flip()

pygame.quit()
