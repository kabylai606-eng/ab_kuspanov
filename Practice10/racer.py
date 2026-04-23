import pygame
import sys
import random
import time
from pathlib import Path
from pygame.locals import *

# ================== INITIALIZATION ==================
pygame.init()  # запускаем все модули pygame (графика, события и т.д.)

# Инициализация звука (может не работать на некоторых ПК)
try:
    pygame.mixer.init()
    SOUND_ENABLED = True
except Exception as e:
    print("Mixer init error:", e)
    SOUND_ENABLED = False

# ================== CONSTANTS ==================
FPS = 60  # кадров в секунду
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
SPEED = 5  # начальная скорость объектов

# Цвета (RGB)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 215, 0)
GOLD = (200, 150, 0)
GRAY = (60, 60, 60)

# ================== GAME STATE ==================
SCORE = 0   # сколько машин уклонились
COINS = 0   # сколько монет собрано

# ================== DISPLAY ==================
DISPLAYSURF = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))  # окно игры
pygame.display.set_caption("Racer – Practice 10")  # заголовок окна

FramePerSec = pygame.time.Clock()  # объект для контроля FPS

# ================== FONTS ==================
font_big = pygame.font.SysFont("Verdana", 60)   # большой текст
font_small = pygame.font.SysFont("Verdana", 20) # маленький текст
game_over_surf = font_big.render("Game Over", True, BLACK)

# ================== PATHS ==================
BASE_DIR = Path(__file__).resolve().parent  # путь к текущему файлу
ASSET_DIR = BASE_DIR / "assets"             # путь к папке assets

# ================== LOAD FUNCTIONS ==================
def load_image_safe(filename, fallback_size, fallback_color, use_alpha=False):
    """Загрузка картинки. Если ошибка — создаётся цветной прямоугольник."""
    full_path = ASSET_DIR / filename
    try:
        image = pygame.image.load(str(full_path))  # загружаем файл
        return image.convert_alpha() if use_alpha else image.convert()
    except Exception as e:
        print(f"Image load error: {full_path} -> {e}")
        surf = pygame.Surface(fallback_size)  # запасной вариант
        surf.fill(fallback_color)
        return surf

def load_sound_safe(filename):
    """Загрузка звука (если не получилось — None)."""
    if not SOUND_ENABLED:
        return None
    full_path = ASSET_DIR / filename
    try:
        return pygame.mixer.Sound(str(full_path))
    except Exception as e:
        print(f"Sound load error: {full_path} -> {e}")
        return None

# ================== LOAD ASSETS ==================
background_img = load_image_safe("AnimatedStreet.png", (SCREEN_WIDTH, SCREEN_HEIGHT), GRAY)
enemy_img = load_image_safe("Enemy.png", (40, 60), RED, use_alpha=True)
player_img = load_image_safe("Player.png", (40, 60), BLUE, use_alpha=True)

# Звук аварии
crash_sound = load_sound_safe("crash.wav")

# Фоновая музыка
if SOUND_ENABLED:
    try:
        pygame.mixer.music.load(str(ASSET_DIR / "background.wav"))
        pygame.mixer.music.play(-1)  # -1 = бесконечно
    except Exception as e:
        print("Music error:", e)

# ================== FALLBACK ROAD ==================
def draw_road(surface):
    """Если фон не загрузился — рисуем дорогу вручную."""
    surface.fill(GRAY)
    pygame.draw.line(surface, YELLOW, (40, 0), (40, SCREEN_HEIGHT), 4)
    pygame.draw.line(surface, YELLOW, (SCREEN_WIDTH - 40, 0), (SCREEN_WIDTH - 40, SCREEN_HEIGHT), 4)

    for y in range(0, SCREEN_HEIGHT, 120):
        pygame.draw.rect(surface, WHITE, (130, y + 20, 18, 70))
        pygame.draw.rect(surface, WHITE, (250, y + 20, 18, 70))

# ================== CLASSES ==================
class Enemy(pygame.sprite.Sprite):
    """Враг (машина, падающая сверху)."""
    def __init__(self):
        super().__init__()
        self.image = enemy_img
        self.rect = self.image.get_rect()
        self._reset_position()

    def _reset_position(self):
        # случайная позиция сверху
        self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), -50)

    def move(self):
        global SCORE
        self.rect.move_ip(0, SPEED)  # движение вниз
        if self.rect.top > SCREEN_HEIGHT:
            SCORE += 1  # игрок увернулся
            self._reset_position()

class Player(pygame.sprite.Sprite):
    """Игрок (управляется стрелками)."""
    def __init__(self):
        super().__init__()
        self.image = player_img
        self.rect = self.image.get_rect()
        self.rect.center = (160, 520)

    def move(self):
        pressed = pygame.key.get_pressed()  # считываем клавиши

        if self.rect.left > 0 and pressed[K_LEFT]:
            self.rect.move_ip(-5, 0)

        if self.rect.right < SCREEN_WIDTH and pressed[K_RIGHT]:
            self.rect.move_ip(5, 0)

class Coin(pygame.sprite.Sprite):
    """Монета (дает очки)."""
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.circle(self.image, YELLOW, (10, 10), 10)
        pygame.draw.circle(self.image, GOLD, (10, 10), 10, 2)

        self.rect = self.image.get_rect()
        self._reset_position()

    def _reset_position(self):
        # случайная позиция выше экрана
        self.rect.center = (
            random.randint(40, SCREEN_WIDTH - 40),
            random.randint(-400, -30)
        )

    def move(self):
        self.rect.move_ip(0, SPEED)
        if self.rect.top > SCREEN_HEIGHT:
            self._reset_position()

# ================== OBJECTS ==================
P1 = Player()  # игрок
E1 = Enemy()   # один враг

coins = pygame.sprite.Group()
for _ in range(3):
    coins.add(Coin())  # создаём 3 монеты

enemies = pygame.sprite.Group(E1)
all_sprites = pygame.sprite.Group(P1, E1)

# ================== EVENTS ==================
INC_SPEED = pygame.USEREVENT + 1
SPAWN_COIN = pygame.USEREVENT + 2

pygame.time.set_timer(INC_SPEED, 1000)   # ускорение каждые 1 сек
pygame.time.set_timer(SPAWN_COIN, 4000)  # новая монета каждые 4 сек

# ================== MAIN LOOP ==================
while True:

    # ===== обработка событий =====
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

        if event.type == INC_SPEED:
            SPEED += 0.5  # увеличиваем сложность

        if event.type == SPAWN_COIN:
            coins.add(Coin())  # добавляем монету

    # ===== фон =====
    DISPLAYSURF.blit(background_img, (0, 0))

    # ===== HUD (очки) =====
    score_surf = font_small.render(f"Score: {SCORE}", True, WHITE)
    coins_surf = font_small.render(f"Coins: {COINS}", True, YELLOW)

    DISPLAYSURF.blit(score_surf, (10, 10))
    DISPLAYSURF.blit(coins_surf, (SCREEN_WIDTH - 120, 10))

    # ===== монеты =====
    for coin in list(coins):
        coin.move()
        DISPLAYSURF.blit(coin.image, coin.rect)

    collected = pygame.sprite.spritecollide(P1, coins, True)
    COINS += len(collected)

    # ===== игрок и враги =====
    for entity in all_sprites:
        entity.move()
        DISPLAYSURF.blit(entity.image, entity.rect)

    # ===== столкновение =====
    if pygame.sprite.spritecollideany(P1, enemies):

        if crash_sound:
            crash_sound.play()  # звук аварии

        time.sleep(0.5)

        # экран Game Over
        DISPLAYSURF.fill(RED)
        DISPLAYSURF.blit(game_over_surf, (30, 220))

        final_score = font_small.render(f"Score: {SCORE} Coins: {COINS}", True, WHITE)
        DISPLAYSURF.blit(final_score, (80, 320))

        pygame.display.update()

        # удаляем все объекты
        for entity in all_sprites:
            entity.kill()

        time.sleep(2)
        pygame.quit()
        sys.exit()

    pygame.display.update()  # обновляем экран
    FramePerSec.tick(FPS)   # ограничиваем FPS