import pygame, sys, random, time
from pygame.locals import *

# Initialise pygame 
pygame.init()

# Constants 
FPS              = 60
SCREEN_WIDTH     = 400
SCREEN_HEIGHT    = 600
SPEED            = 5          # current fall speed (global, increases over time)

ENEMY_BOOST_EVERY = 5         # enemy gets faster every N coins collected

# Colors 
BLACK   = (0,   0,   0)
WHITE   = (255, 255, 255)
RED     = (220, 50,  50)
BLUE    = (0,   0,   255)
GRAY    = (60,  60,  60)

# Coin tier colors
BRONZE_COLOR = (205, 127, 50)
SILVER_COLOR = (192, 192, 192)
GOLD_COLOR   = (255, 215, 0)

# Game state 
SCORE          = 0    # enemies dodged
TOTAL_COINS    = 0    # total coin value collected
ENEMY_BOOSTS   = 0    # how many times the enemy speed was boosted

# Display & clock 
DISPLAYSURF = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Racer – Practice 11")
FramePerSec = pygame.time.Clock()

# Fonts 
font_big   = pygame.font.SysFont("Verdana", 60)
font_small = pygame.font.SysFont("Verdana", 18)
game_over_surf = font_big.render("Game Over", True, BLACK)

# Assets 
ASSET_DIR = "assets/"

def load_image_safe(path, fallback_size, fallback_color):
    """Load an image, or return a solid-color rectangle if missing."""
    try:
        return pygame.image.load(path)
    except Exception:
        surf = pygame.Surface(fallback_size)
        surf.fill(fallback_color)
        return surf

background_img = load_image_safe(ASSET_DIR + "AnimatedStreet.png", (SCREEN_WIDTH, SCREEN_HEIGHT), GRAY)
enemy_img      = load_image_safe(ASSET_DIR + "Enemy.png",           (40, 60), RED)
player_img     = load_image_safe(ASSET_DIR + "Player.png",          (40, 60), BLUE)


# Coin tiers 
# Each tier is: (label, value, color, spawn_weight)
# spawn_weight controls how often this tier appears (higher = more common)
COIN_TIERS = [
    {"label": "+1", "value": 1, "color": BRONZE_COLOR, "weight": 60},
    {"label": "+3", "value": 3, "color": SILVER_COLOR, "weight": 30},
    {"label": "+5", "value": 5, "color": GOLD_COLOR,   "weight": 10},
]


def pick_random_tier():
    """Choose a coin tier based on spawn weights (weighted random)."""
    total  = sum(t["weight"] for t in COIN_TIERS)
    rnd    = random.randint(1, total)
    cumul  = 0
    for tier in COIN_TIERS:
        cumul += tier["weight"]
        if rnd <= cumul:
            return tier
    return COIN_TIERS[0]   # fallback


# Sprite classes 

class Enemy(pygame.sprite.Sprite):
    """Enemy car that falls from the top; speed is driven by global SPEED."""
    def __init__(self):
        super().__init__()
        self.image = enemy_img
        self.rect  = self.image.get_rect()
        self._reset()

    def _reset(self):
        self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), 0)

    def move(self):
        global SCORE
        self.rect.move_ip(0, SPEED)
        if self.rect.bottom > SCREEN_HEIGHT:
            SCORE += 1
            self._reset()


class Player(pygame.sprite.Sprite):
    """Player car controlled with arrow keys."""
    def __init__(self):
        super().__init__()
        self.image = player_img
        self.rect  = self.image.get_rect()
        self.rect.center = (160, 520)

    def move(self):
        pressed = pygame.key.get_pressed()
        if self.rect.left  > 0              and pressed[K_LEFT]:
            self.rect.move_ip(-5, 0)
        if self.rect.right < SCREEN_WIDTH   and pressed[K_RIGHT]:
            self.rect.move_ip(5, 0)


class Coin(pygame.sprite.Sprite):
    """
    Coin with a randomly chosen tier.
    Higher-value coins are rarer (controlled by spawn weights).
    """
    def __init__(self):
        super().__init__()
        self.tier  = pick_random_tier()          # Bronze / Silver / Gold
        self.value = self.tier["value"]

        # Draw the coin: circle + value label
        self.image = pygame.Surface((24, 24), pygame.SRCALPHA)
        pygame.draw.circle(self.image, self.tier["color"], (12, 12), 11)
        pygame.draw.circle(self.image, BLACK,               (12, 12), 11, 1)
        lbl = pygame.font.SysFont("Verdana", 9, bold=True).render(
            self.tier["label"], True, BLACK
        )
        self.image.blit(lbl, lbl.get_rect(center=(12, 12)))

        self.rect = self.image.get_rect()
        self._reset()

    def _reset(self):
        self.rect.center = (
            random.randint(40, SCREEN_WIDTH - 40),
            random.randint(-400, -30)
        )

    def move(self):
        self.rect.move_ip(0, SPEED)
        if self.rect.top > SCREEN_HEIGHT:
            # Re-pick a new tier when the coin respawns
            old_tier = self.tier
            self.tier  = pick_random_tier()
            self.value = self.tier["value"]

            if self.tier["label"] != old_tier["label"]:
                # Redraw the coin surface for the new tier
                self.image.fill((0, 0, 0, 0))
                pygame.draw.circle(self.image, self.tier["color"], (12, 12), 11)
                pygame.draw.circle(self.image, BLACK,               (12, 12), 11, 1)
                lbl = pygame.font.SysFont("Verdana", 9, bold=True).render(
                    self.tier["label"], True, BLACK
                )
                self.image.blit(lbl, lbl.get_rect(center=(12, 12)))

            self._reset()


# Sprite setup 
P1 = Player()
E1 = Enemy()

coins = pygame.sprite.Group()
for _ in range(4):           # start with 4 coins on screen
    coins.add(Coin())

enemies     = pygame.sprite.Group(E1)
all_sprites = pygame.sprite.Group(P1, E1)

# Custom timer events 
INC_SPEED  = pygame.USEREVENT + 1
SPAWN_COIN = pygame.USEREVENT + 2
pygame.time.set_timer(INC_SPEED,  1000)   # speed up every second
pygame.time.set_timer(SPAWN_COIN, 5000)   # spawn extra coin every 5 s

# Main game loop 
while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == INC_SPEED:
            SPEED += 0.5
        if event.type == SPAWN_COIN:
            coins.add(Coin())

    # Background 
    DISPLAYSURF.blit(background_img, (0, 0))

    # HUD 
    score_surf  = font_small.render(f"Score: {SCORE}", True, WHITE)
    coins_surf  = font_small.render(f"Coins: {TOTAL_COINS}", True, GOLD_COLOR)
    boost_surf  = font_small.render(f"Enemy boosts: {ENEMY_BOOSTS}", True, (255, 100, 100))
    DISPLAYSURF.blit(score_surf,  (10, 10))
    DISPLAYSURF.blit(coins_surf,  (SCREEN_WIDTH - 130, 10))
    DISPLAYSURF.blit(boost_surf,  (SCREEN_WIDTH - 165, 34))

    # Coin-tier legend (bottom-left)
    legend_y = SCREEN_HEIGHT - 70
    for tier in COIN_TIERS:
        pygame.draw.circle(DISPLAYSURF, tier["color"], (15, legend_y), 7)
        lbl = font_small.render(f"= {tier['value']} pt{'s' if tier['value']>1 else ''}", True, WHITE)
        DISPLAYSURF.blit(lbl, (26, legend_y - 9))
        legend_y += 22

    # Coins: move, draw, collect 
    for coin in list(coins):
        coin.move()
        DISPLAYSURF.blit(coin.image, coin.rect)

    collected = pygame.sprite.spritecollide(P1, coins, True)
    for coin in collected:
        TOTAL_COINS += coin.value

        # Check if we hit the next boost threshold
        new_boosts = TOTAL_COINS // ENEMY_BOOST_EVERY
        if new_boosts > ENEMY_BOOSTS:
            ENEMY_BOOSTS = new_boosts
            SPEED += 1.5    # significant speed jump for the enemy
            # Spawn a replacement coin
            coins.add(Coin())

    # Main sprites 
    for entity in all_sprites:
        entity.move()
        DISPLAYSURF.blit(entity.image, entity.rect)

    # Collision with enemy 
    if pygame.sprite.spritecollideany(P1, enemies):
        try:
            pygame.mixer.Sound(ASSET_DIR + "crash.wav").play()
        except Exception:
            pass
        time.sleep(0.5)

        DISPLAYSURF.fill(RED)
        DISPLAYSURF.blit(game_over_surf, (30, 200))

        lines = [
            f"Score: {SCORE}",
            f"Coins collected: {TOTAL_COINS}",
            f"Enemy boosts earned: {ENEMY_BOOSTS}",
        ]
        for i, line in enumerate(lines):
            surf = font_small.render(line, True, WHITE)
            DISPLAYSURF.blit(surf, (80, 290 + i * 30))

        pygame.display.update()
        for entity in all_sprites:
            entity.kill()
        time.sleep(2)
        pygame.quit()
        sys.exit()

    pygame.display.update()
    FramePerSec.tick(FPS)