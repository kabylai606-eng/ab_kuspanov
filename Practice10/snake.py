import pygame, sys, random
from pygame.locals import *

# Initialise pygame 
pygame.init()

# Constants 
CELL        = 20           # size of one grid cell in pixels
COLS        = 30           # number of columns
ROWS        = 30           # number of rows
WIDTH       = COLS * CELL  # screen width  (600 px)
HEIGHT      = ROWS * CELL  # screen height (600 px)

FOODS_PER_LEVEL = 4        # foods needed to advance to the next level

# Direction vectors
UP    = (0, -1)
DOWN  = (0,  1)
LEFT  = (-1, 0)
RIGHT = (1,  0)

# Colors 
BLACK      = (0,   0,   0)
WHITE      = (255, 255, 255)
GREEN      = (50,  200, 50)
DARK_GREEN = (30,  130, 30)
RED        = (220, 50,  50)
GRAY       = (40,  40,  40)
WALL_COLOR = (80,  80,  80)
GOLD       = (255, 215, 0)

# Display 
DISPLAYSURF = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake – Practice 10")

# Fonts
font_hud = pygame.font.SysFont("Verdana", 18)
font_big = pygame.font.SysFont("Verdana", 48)


#  Helper functions 

def is_wall(col, row):
    """Return True if the cell is a border wall."""
    return col == 0 or row == 0 or col == COLS - 1 or row == ROWS - 1


def random_food_position(snake_body):
    """
    Return a grid cell (col, row) that is:
      • not on a wall
      • not occupied by the snake body
    """
    while True:
        col = random.randint(1, COLS - 2)
        row = random.randint(1, ROWS - 2)
        if (col, row) not in snake_body:
            return col, row


def draw_grid():
    """Draw a subtle grid and the border walls."""
    for c in range(COLS):
        for r in range(ROWS):
            rect = pygame.Rect(c * CELL, r * CELL, CELL, CELL)
            if is_wall(c, r):
                pygame.draw.rect(DISPLAYSURF, WALL_COLOR, rect)
            else:
                pygame.draw.rect(DISPLAYSURF, GRAY, rect)
            pygame.draw.rect(DISPLAYSURF, BLACK, rect, 1)   # grid lines


def draw_snake(snake):
    """Draw each segment of the snake."""
    for i, (c, r) in enumerate(snake):
        color = DARK_GREEN if i == 0 else GREEN   # head is darker
        rect  = pygame.Rect(c * CELL + 1, r * CELL + 1, CELL - 2, CELL - 2)
        pygame.draw.rect(DISPLAYSURF, color, rect)


def draw_food(food_pos):
    """Draw the food as a red circle."""
    c, r   = food_pos
    center = (c * CELL + CELL // 2, r * CELL + CELL // 2)
    pygame.draw.circle(DISPLAYSURF, RED, center, CELL // 2 - 2)


def draw_hud(score, level, foods_until_next):
    """Render the HUD: score and level."""
    hud_score = font_hud.render(f"Score: {score}", True, WHITE)
    hud_level = font_hud.render(f"Level: {level}", True, GOLD)
    hud_next  = font_hud.render(f"Next lvl in: {foods_until_next}", True, WHITE)
    DISPLAYSURF.blit(hud_score, (CELL + 5, 5))
    DISPLAYSURF.blit(hud_level, (CELL + 5, 28))
    DISPLAYSURF.blit(hud_next,  (WIDTH - 160, 5))


def game_over_screen(score, level):
    """Show game-over overlay and wait for a key press."""
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    DISPLAYSURF.blit(overlay, (0, 0))

    go_surf   = font_big.render("GAME OVER", True, RED)
    sc_surf   = font_hud.render(f"Score: {score}   Level: {level}", True, WHITE)
    cont_surf = font_hud.render("Press any key to quit", True, WHITE)

    DISPLAYSURF.blit(go_surf,   go_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 60)))
    DISPLAYSURF.blit(sc_surf,   sc_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
    DISPLAYSURF.blit(cont_surf, cont_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50)))
    pygame.display.update()

    waiting = True
    while waiting:
        for ev in pygame.event.get():
            if ev.type in (QUIT, KEYDOWN):
                waiting = False


# Game state 
snake  = [(COLS // 2, ROWS // 2),
          (COLS // 2 - 1, ROWS // 2),
          (COLS // 2 - 2, ROWS // 2)]   # starts moving right
direction      = RIGHT
next_direction = RIGHT

score          = 0
level          = 1
foods_eaten    = 0   # within the current level

# Place first food
food = random_food_position(snake)

# Speed: base delay between moves in milliseconds
BASE_SPEED_MS = 200

MOVE_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(MOVE_EVENT, BASE_SPEED_MS)

clock = pygame.time.Clock()

# Main game loop 
running = True
while running:
    clock.tick(60)

    # --- Event handling ---
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

        # Arrow key input – prevent reversing direction
        if event.type == KEYDOWN:
            if event.key == K_UP    and direction != DOWN:
                next_direction = UP
            elif event.key == K_DOWN  and direction != UP:
                next_direction = DOWN
            elif event.key == K_LEFT  and direction != RIGHT:
                next_direction = LEFT
            elif event.key == K_RIGHT and direction != LEFT:
                next_direction = RIGHT

        # Snake movement driven by a timed event
        if event.type == MOVE_EVENT:
            direction = next_direction
            head_c, head_r = snake[0]
            dc, dr         = direction
            new_head       = (head_c + dc, head_r + dr)

            # ── Wall collision ──
            if is_wall(*new_head):
                game_over_screen(score, level)
                running = False
                break

            # ── Self collision ──
            if new_head in snake[1:]:
                game_over_screen(score, level)
                running = False
                break

            # Move snake: prepend new head 
            snake.insert(0, new_head)

            # Food eaten?
            if new_head == food:
                score       += 10 * level          # more points at higher levels
                foods_eaten += 1

                # Check if we should advance to the next level
                if foods_eaten >= FOODS_PER_LEVEL:
                    level       += 1
                    foods_eaten  = 0
                    # Increase speed by reducing the move interval
                    new_delay = max(60, BASE_SPEED_MS - (level - 1) * 25)
                    pygame.time.set_timer(MOVE_EVENT, new_delay)

                # Spawn food away from walls and snake
                food = random_food_position(snake)
            else:
                snake.pop()   # remove tail (snake did not grow)

    if not running:
        break

    # Drawing 
    draw_grid()
    draw_food(food)
    draw_snake(snake)
    draw_hud(score, level, FOODS_PER_LEVEL - foods_eaten)
    pygame.display.update()

pygame.quit()
sys.exit()