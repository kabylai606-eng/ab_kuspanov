import pygame, sys, random, time
from pygame.locals import *

# Initialise pygame
pygame.init()

# Constants
FPS           = 60
SCREEN_WIDTH  = 400
SCREEN_HEIGHT = 600
SPEED         = 5          # initial enemy / coin fall speed

# Colors
BLACK  = (0,   0,   0)
WHITE  = (255, 255, 255)
RED    = (255, 0,   0)
BLUE   = (0,   0,   255)
YELLOW = (255, 215, 0)
GOLD   = (200, 150, 0)
GRAY   = (60,  60,  60)

# Game state
SCORE = 0     # enemies dodged
COINS = 0     # coins collected

#  Display 
DISPLAYSURF = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Racer – Practice 10")

# Clock
FramePerSec = pygame.time.Clock()

# Fonts 
font_big   = pygame.font.SysFont("Verdana", 60)
font_small = pygame.font.SysFont("Verdana", 20)
game_over_surf = font_big.render("Game Over", True, BLACK)

# Asset loading (with fallback if files are missing) 
ASSET_DIR = "assets/"

def load_image_safe(path, fallback_size, fallback_color):
    """Try to load an image; return a coloured rectangle on failure."""
    try:
        return pygame.image.load(path)
    except Exception:
        surf = pygame.Surface(fallback_size)
        surf.fill(fallback_color)
        return surf

background_img = load_image_safe(ASSET_DIR + "AnimatedStreet.png", (SCREEN_WIDTH, SCREEN_HEIGHT), GRAY)
enemy_img      = load_image_safe(ASSET_DIR + "Enemy.png",           (40, 60), RED)
player_img     = load_image_safe(ASSET_DIR + "Player.png",          (40, 60), BLUE)


def draw_road(surface):
    """Fallback road drawn with pygame primitives."""
    surface.fill(GRAY)
    for y in range(0, SCREEN_HEIGHT, 60):
        pygame.draw.rect(surface, WHITE, (195, y, 10, 40))


# Sprite classes 

class Enemy(pygame.sprite.Sprite):
    """Enemy car that falls from the top of the screen."""
    def __init__(self):
        super().__init__()
        self.image = enemy_img
        self.rect  = self.image.get_rect()
        self._reset_position()

    def _reset_position(self):
        """Place the enemy at a random horizontal position at the top."""
        self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), 0)

    def move(self):
        global SCORE
        self.rect.move_ip(0, SPEED)         # move downward
        if self.rect.bottom > SCREEN_HEIGHT:
            SCORE += 1                       # player dodged this car
            self._reset_position()


class Player(pygame.sprite.Sprite):
    """Player car controlled with arrow keys."""
    def __init__(self):
        super().__init__()
        self.image = player_img
        self.rect  = self.image.get_rect()
        self.rect.center = (160, 520)

    def move(self):
        pressed = pygame.key.get_pressed()
        # Move left while staying within screen bounds
        if self.rect.left > 0 and pressed[K_LEFT]:
            self.rect.move_ip(-5, 0)
        # Move right while staying within screen bounds
        if self.rect.right < SCREEN_WIDTH and pressed[K_RIGHT]:
            self.rect.move_ip(5, 0)


class Coin(pygame.sprite.Sprite):
    """Coin that appears randomly on the road and falls downward."""
    def __init__(self):
        super().__init__()
        # Draw a golden circle as the coin sprite
        self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.circle(self.image, YELLOW, (10, 10), 10)
        pygame.draw.circle(self.image, GOLD,   (10, 10), 10, 2)

        self.rect = self.image.get_rect()
        self._reset_position()

    def _reset_position(self):
        """Spawn coin at random position above the visible screen."""
        self.rect.center = (
            random.randint(40, SCREEN_WIDTH - 40),
            random.randint(-400, -30)
        )

    def move(self):
        self.rect.move_ip(0, SPEED)
        if self.rect.top > SCREEN_HEIGHT:   # coin left the screen → respawn
            self._reset_position()


# Sprite setup
P1 = Player()
E1 = Enemy()

# Three coins visible on screen at start
coins = pygame.sprite.Group()
for _ in range(3):
    coins.add(Coin())

enemies    = pygame.sprite.Group(E1)
all_sprites = pygame.sprite.Group(P1, E1)

# Custom events 
INC_SPEED  = pygame.USEREVENT + 1
SPAWN_COIN = pygame.USEREVENT + 2
pygame.time.set_timer(INC_SPEED,  1000)   # increase speed every second
pygame.time.set_timer(SPAWN_COIN, 4000)   # spawn an extra coin every 4 s

# Main game loop 
while True:
    # Event handling 
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == INC_SPEED:
            SPEED += 0.5                   # gradually get harder
        if event.type == SPAWN_COIN:
            coins.add(Coin())              # add a new random coin

    # Background 
    DISPLAYSURF.blit(background_img, (0, 0))

    # HUD: score (top left) and coins (top right) 
    score_surf = font_small.render(f"Score: {SCORE}", True, WHITE)
    coins_surf = font_small.render(f"Coins: {COINS}", True, YELLOW)
    DISPLAYSURF.blit(score_surf, (10, 10))
    DISPLAYSURF.blit(coins_surf, (SCREEN_WIDTH - 120, 10))   # top-right corner

    # Coins: move, draw, collect 
    for coin in list(coins):
        coin.move()
        DISPLAYSURF.blit(coin.image, coin.rect)

    collected = pygame.sprite.spritecollide(P1, coins, True)  # remove on hit
    COINS += len(collected)

    # Main sprites: move and draw 
    for entity in all_sprites:
        entity.move()
        DISPLAYSURF.blit(entity.image, entity.rect)

    # Collision with enemy = Game Over 
    if pygame.sprite.spritecollideany(P1, enemies):
        try:
            pygame.mixer.Sound(ASSET_DIR + "crash.wav").play()
        except Exception:
            pass
        time.sleep(0.5)

        DISPLAYSURF.fill(RED)
        DISPLAYSURF.blit(game_over_surf, (30, 220))
        final_score = font_small.render(f"Score: {SCORE}   Coins: {COINS}", True, WHITE)
        DISPLAYSURF.blit(final_score, (80, 320))
        pygame.display.update()

        for entity in all_sprites:
            entity.kill()
        time.sleep(2)
        pygame.quit()
        sys.exit()

    pygame.display.update()
    FramePerSec.tick(FPS)