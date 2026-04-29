import pygame, sys, random, time as pytime
from pygame.locals import *

# Initialise pygame 
pygame.init()

# Constants 
CELL        = 20
COLS        = 30
ROWS        = 30
WIDTH       = COLS * CELL   # 600 px
HEIGHT      = ROWS * CELL   # 600 px

FOODS_PER_LEVEL = 4         # foods required to level up

# Directions
UP    = (0, -1)
DOWN  = (0,  1)
LEFT  = (-1, 0)
RIGHT = (1,  0)

# Colors 
BLACK      = (0,   0,   0)
WHITE      = (255, 255, 255)
GREEN      = (50,  200, 50)
DARK_GREEN = (30,  130, 30)
GRAY       = (40,  40,  40)
WALL_COLOR = (80,  80,  80)
GOLD       = (255, 215, 0)

# Food tier colors
COMMON_COLOR    = (220, 50,  50)    # red  – common
RARE_COLOR      = (50,  100, 255)   # blue – rare
LEGENDARY_COLOR = (220, 180, 0)     # gold – legendary

# Food tiers 
# Each tier: points, color, spawn weight, timeout in seconds
FOOD_TIERS = [
    {"name": "Common",    "pts": 10, "color": COMMON_COLOR,    "weight": 60, "timeout": 10},
    {"name": "Rare",      "pts": 30, "color": RARE_COLOR,      "weight": 30, "timeout":  7},
    {"name": "Legendary", "pts": 50, "color": LEGENDARY_COLOR, "weight": 10, "timeout":  4},
]


def pick_food_tier():
    """Weighted-random selection of a food tier."""
    total = sum(t["weight"] for t in FOOD_TIERS)
    rnd   = random.randint(1, total)
    cumul = 0
    for tier in FOOD_TIERS:
        cumul += tier["weight"]
        if rnd <= cumul:
            return tier
    return FOOD_TIERS[0]


# Display 
DISPLAYSURF = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake – Practice 11")

# Fonts 
font_hud   = pygame.font.SysFont("Verdana", 18)
font_small = pygame.font.SysFont("Verdana", 14)
font_big   = pygame.font.SysFont("Verdana", 48)


# Helper functions 

def is_wall(col, row):
    """Return True if the cell is a border wall."""
    return col == 0 or row == 0 or col == COLS - 1 or row == ROWS - 1


def random_food_position(snake_body, excluded=None):
    """
    Return (col, row) that is not a wall, not on the snake, and not in excluded.
    excluded – set of positions already used by other food items.
    """
    excluded = excluded or set()
    while True:
        col = random.randint(1, COLS - 2)
        row = random.randint(1, ROWS - 2)
        if (col, row) not in snake_body and (col, row) not in excluded:
            return col, row


def draw_grid():
    """Draw the grid with walls."""
    for c in range(COLS):
        for r in range(ROWS):
            rect = pygame.Rect(c * CELL, r * CELL, CELL, CELL)
            pygame.draw.rect(DISPLAYSURF, WALL_COLOR if is_wall(c, r) else GRAY, rect)
            pygame.draw.rect(DISPLAYSURF, BLACK, rect, 1)


def draw_snake(snake):
    """Draw the snake body on screen."""
    for i, (c, r) in enumerate(snake):
        color = DARK_GREEN if i == 0 else GREEN
        rect  = pygame.Rect(c * CELL + 1, r * CELL + 1, CELL - 2, CELL - 2)
        pygame.draw.rect(DISPLAYSURF, color, rect)


def draw_food_items(food_items, now):
    """
    Draw all active food items.
    Each item shows a coloured circle and a countdown timer.
    """
    for item in food_items:
        c, r    = item["pos"]
        tier    = item["tier"]
        elapsed = now - item["spawn_time"]
        remaining = max(0, tier["timeout"] - elapsed)

        cx = c * CELL + CELL // 2
        cy = r * CELL + CELL // 2

        # Draw the food circle
        pygame.draw.circle(DISPLAYSURF, tier["color"], (cx, cy), CELL // 2 - 1)

        # Draw a shrinking timer arc around the food
        if remaining > 0:
            fraction = remaining / tier["timeout"]
            arc_rect = pygame.Rect(c * CELL, r * CELL, CELL, CELL)
            # Draw a thin white arc showing time remaining
            import math
            end_angle = 2 * math.pi * fraction
            pygame.draw.arc(DISPLAYSURF, WHITE, arc_rect, 0, end_angle, 2)

        # Show point value
        pts_surf = font_small.render(f"+{tier['pts']}", True, WHITE)
        DISPLAYSURF.blit(pts_surf, pts_surf.get_rect(center=(cx, cy)))


def draw_hud(score, level, foods_eaten, total_foods_for_level):
    """Render score, level and progress HUD."""
    DISPLAYSURF.blit(font_hud.render(f"Score: {score}", True, WHITE),   (CELL + 5, 5))
    DISPLAYSURF.blit(font_hud.render(f"Level: {level}", True, GOLD),    (CELL + 5, 28))
    next_txt = f"Next lvl: {total_foods_for_level - foods_eaten} food"
    DISPLAYSURF.blit(font_hud.render(next_txt, True, WHITE), (WIDTH - 220, 5))

    # Food tier legend
    legend_y = HEIGHT - 70
    for tier in FOOD_TIERS:
        pygame.draw.circle(DISPLAYSURF, tier["color"], (CELL + 10, legend_y), 7)
        lbl = font_small.render(
            f"{tier['name']}: +{tier['pts']} pts ({tier['timeout']}s)", True, WHITE
        )
        DISPLAYSURF.blit(lbl, (CELL + 22, legend_y - 8))
        legend_y += 22


def game_over_screen(score, level):
    """Semi-transparent game-over overlay."""
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    DISPLAYSURF.blit(overlay, (0, 0))

    DISPLAYSURF.blit(
        font_big.render("GAME OVER", True, (220, 50, 50)),
        font_big.render("GAME OVER", True, (220, 50, 50)).get_rect(center=(WIDTH // 2, HEIGHT // 2 - 60))
    )
    sc_surf  = font_hud.render(f"Score: {score}   Level: {level}", True, WHITE)
    cnt_surf = font_hud.render("Press any key to quit", True, WHITE)
    DISPLAYSURF.blit(sc_surf,  sc_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
    DISPLAYSURF.blit(cnt_surf, cnt_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50)))
    pygame.display.update()

    waiting = True
    while waiting:
        for ev in pygame.event.get():
            if ev.type in (QUIT, KEYDOWN):
                waiting = False


# Game state 
snake          = [(COLS // 2, ROWS // 2),
                  (COLS // 2 - 1, ROWS // 2),
                  (COLS // 2 - 2, ROWS // 2)]
direction      = RIGHT
next_direction = RIGHT

score          = 0
level          = 1
foods_eaten    = 0    # within current level

BASE_SPEED_MS  = 200

MOVE_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(MOVE_EVENT, BASE_SPEED_MS)

# Multiple food items on screen 
# Each item is a dict: { "pos": (c,r), "tier": {...}, "spawn_time": float }
food_items = []

def add_food_item(snake_body, existing_food):
    """Spawn a new food item at a position not occupied by the snake or other food."""
    excluded = {item["pos"] for item in existing_food}
    pos      = random_food_position(snake_body, excluded)
    food_items.append({
        "pos":        pos,
        "tier":       pick_food_tier(),
        "spawn_time": pytime.time(),
    })

# Start with 2 food items
add_food_item(snake, food_items)
add_food_item(snake, food_items)

clock   = pygame.time.Clock()
running = True

# Main loop 
while running:
    clock.tick(60)
    now = pytime.time()

    # Remove expired food items (disappeared after timeout) 
    active_food = []
    for item in food_items:
        if now - item["spawn_time"] < item["tier"]["timeout"]:
            active_food.append(item)
    food_items = active_food

    # Keep at least 1 food on screen at all times
    if len(food_items) == 0:
        add_food_item(snake, food_items)

    # Event handling 
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

        if event.type == KEYDOWN:
            if event.key == K_UP    and direction != DOWN:
                next_direction = UP
            elif event.key == K_DOWN  and direction != UP:
                next_direction = DOWN
            elif event.key == K_LEFT  and direction != RIGHT:
                next_direction = LEFT
            elif event.key == K_RIGHT and direction != LEFT:
                next_direction = RIGHT

        if event.type == MOVE_EVENT:
            direction       = next_direction
            head_c, head_r  = snake[0]
            dc, dr          = direction
            new_head        = (head_c + dc, head_r + dr)

            # Wall collision
            if is_wall(*new_head):
                game_over_screen(score, level)
                running = False
                break

            # Self collision
            if new_head in snake[1:]:
                game_over_screen(score, level)
                running = False
                break

            snake.insert(0, new_head)

            # Check if snake ate any food item
            ate_food = False
            for item in food_items:
                if new_head == item["pos"]:
                    score       += item["tier"]["pts"] * level
                    foods_eaten += 1
                    ate_food     = True
                    food_items.remove(item)

                    # Replace the eaten food with a fresh one
                    add_food_item(snake, food_items)

                    # Level up?
                    if foods_eaten >= FOODS_PER_LEVEL:
                        level       += 1
                        foods_eaten  = 0
                        new_delay    = max(60, BASE_SPEED_MS - (level - 1) * 25)
                        pygame.time.set_timer(MOVE_EVENT, new_delay)
                        # Bonus: extra food on higher levels
                        if len(food_items) < level + 1:
                            add_food_item(snake, food_items)
                    break

            if not ate_food:
                snake.pop()   # no food eaten → remove tail

    if not running:
        break

    # Drawing
    draw_grid()
    draw_food_items(food_items, now)
    draw_snake(snake)
    draw_hud(score, level, foods_eaten, FOODS_PER_LEVEL)
    pygame.display.update()

pygame.quit()
sys.exit()