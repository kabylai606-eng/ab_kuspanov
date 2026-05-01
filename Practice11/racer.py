import pygame
import sys
import random
import time
from pathlib import Path
from pygame.locals import *

pygame.init()  # запускаем pygame

# путь к папке проекта
BASE_DIR = Path(__file__).resolve().parent

# путь к папке assets
ASSETS = BASE_DIR / "assets"

# основные настройки окна и игры
FPS = 60
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
SPEED = 5  # начальная скорость

ENEMY_BOOST_EVERY = 5  # ускорение после каждых 5 монет

# цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (220, 50, 50)
BLUE = (0, 0, 255)
GRAY = (60, 60, 60)

# цвета монет
BRONZE_COLOR = (205, 127, 50)
SILVER_COLOR = (192, 192, 192)
GOLD_COLOR = (255, 215, 0)

# игровые значения
SCORE = 0          # очки за объезд врагов
TOTAL_COINS = 0    # сумма собранных монет
ENEMY_BOOSTS = 0   # количество ускорений

# создание окна
DISPLAYSURF = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Racer – Practice 11")
FramePerSec = pygame.time.Clock()

# шрифты для текста
font_big = pygame.font.SysFont("Verdana", 55)
font_small = pygame.font.SysFont("Verdana", 18)
game_over_surf = font_big.render("Game Over", True, BLACK)


# безопасная загрузка картинки
def load_image_safe(path, fallback_size, fallback_color):
    try:
        image = pygame.image.load(path).convert_alpha()
        return image
    except Exception:
        # если картинка не найдена, создается цветной прямоугольник
        surf = pygame.Surface(fallback_size, pygame.SRCALPHA)
        surf.fill(fallback_color)
        return surf


# загрузка фона
background_img = load_image_safe(
    ASSETS / "AnimatedStreet.png",
    (SCREEN_WIDTH, SCREEN_HEIGHT),
    GRAY
)
background_img = pygame.transform.scale(
    background_img,
    (SCREEN_WIDTH, SCREEN_HEIGHT)
)

# загрузка машины врага
enemy_img = load_image_safe(
    ASSETS / "Enemy.png",
    (45, 75),
    RED
)
enemy_img = pygame.transform.scale(enemy_img, (45, 75))

# загрузка машины игрока
player_img = load_image_safe(
    ASSETS / "Player.png",
    (50, 90),
    BLUE
)
player_img = pygame.transform.scale(player_img, (50, 90))


# загрузка фоновой музыки
try:
    pygame.mixer.init()
    pygame.mixer.music.load(ASSETS / "background.wav")
    pygame.mixer.music.play(-1)  # музыка играет бесконечно
except Exception:
    pass  # если звук не работает, игра все равно запускается


# типы монет
COIN_TIERS = [
    {"label": "+1", "value": 1, "color": BRONZE_COLOR, "weight": 60},
    {"label": "+3", "value": 3, "color": SILVER_COLOR, "weight": 30},
    {"label": "+5", "value": 5, "color": GOLD_COLOR, "weight": 10},
]


# выбор случайной монеты по весу
def pick_random_tier():
    total = sum(t["weight"] for t in COIN_TIERS)
    rnd = random.randint(1, total)
    current = 0

    for tier in COIN_TIERS:
        current += tier["weight"]
        if rnd <= current:
            return tier

    return COIN_TIERS[0]


# класс машины-врага
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = enemy_img
        self.rect = self.image.get_rect()
        self.reset()

    def reset(self):
        # враг появляется сверху в случайном месте
        self.rect.center = (
            random.randint(40, SCREEN_WIDTH - 40),
            -60
        )

    def move(self):
        global SCORE

        # движение вниз
        self.rect.move_ip(0, SPEED)

        # если враг вышел за экран
        if self.rect.top > SCREEN_HEIGHT:
            SCORE += 1
            self.reset()


# класс машины игрока
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_img
        self.rect = self.image.get_rect()
        self.rect.center = (
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT - 80
        )

    def move(self):
        pressed = pygame.key.get_pressed()

        # движение влево
        if pressed[K_LEFT] and self.rect.left > 0:
            self.rect.move_ip(-5, 0)

        # движение вправо
        if pressed[K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.move_ip(5, 0)


# класс монеты
class Coin(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        # выбираем тип монеты
        self.tier = pick_random_tier()
        self.value = self.tier["value"]

        # создаем поверхность монеты
        self.image = pygame.Surface((24, 24), pygame.SRCALPHA)
        self.draw_coin()

        self.rect = self.image.get_rect()
        self.reset()

    def draw_coin(self):
        # очищаем монету
        self.image.fill((0, 0, 0, 0))

        # рисуем круг монеты
        pygame.draw.circle(self.image, self.tier["color"], (12, 12), 11)
        pygame.draw.circle(self.image, BLACK, (12, 12), 11, 1)

        # пишем значение монеты
        label = pygame.font.SysFont("Verdana", 9, bold=True).render(
            self.tier["label"],
            True,
            BLACK
        )
        self.image.blit(label, label.get_rect(center=(12, 12)))

    def reset(self):
        # монета появляется сверху
        self.rect.center = (
            random.randint(40, SCREEN_WIDTH - 40),
            random.randint(-500, -30)
        )

    def move(self):
        # движение монеты вниз
        self.rect.move_ip(0, SPEED)

        # если монета вышла за экран
        if self.rect.top > SCREEN_HEIGHT:
            self.tier = pick_random_tier()
            self.value = self.tier["value"]
            self.draw_coin()
            self.reset()


# создание игрока и врага
P1 = Player()
E1 = Enemy()

# группа монет
coins = pygame.sprite.Group()
for _ in range(4):
    coins.add(Coin())

# группы спрайтов
enemies = pygame.sprite.Group(E1)
all_sprites = pygame.sprite.Group(P1, E1)

# события таймера
INC_SPEED = pygame.USEREVENT + 1
SPAWN_COIN = pygame.USEREVENT + 2

pygame.time.set_timer(INC_SPEED, 1000)   # каждую секунду ускорение
pygame.time.set_timer(SPAWN_COIN, 5000)  # каждые 5 секунд новая монета


# главный игровой цикл
while True:
    # обработка событий
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

        # постепенное ускорение игры
        if event.type == INC_SPEED:
            SPEED += 0.2

        # появление новой монеты
        if event.type == SPAWN_COIN:
            coins.add(Coin())

    # рисуем фон
    DISPLAYSURF.blit(background_img, (0, 0))

    # создаем текст HUD
    score_surf = font_small.render(f"Score: {SCORE}", True, WHITE)
    coins_surf = font_small.render(f"Coins: {TOTAL_COINS}", True, GOLD_COLOR)
    boost_surf = font_small.render(f"Enemy boosts: {ENEMY_BOOSTS}", True, WHITE)

    # показываем HUD
    DISPLAYSURF.blit(score_surf, (10, 10))
    DISPLAYSURF.blit(coins_surf, (260, 10))
    DISPLAYSURF.blit(boost_surf, (210, 35))

    # движение и отображение монет
    for coin in list(coins):
        coin.move()
        DISPLAYSURF.blit(coin.image, coin.rect)

    # проверка сбора монет игроком
    collected = pygame.sprite.spritecollide(P1, coins, True)

    for coin in collected:
        TOTAL_COINS += coin.value

        # проверка ускорения врага
        new_boosts = TOTAL_COINS // ENEMY_BOOST_EVERY

        if new_boosts > ENEMY_BOOSTS:
            ENEMY_BOOSTS = new_boosts
            SPEED += 1.0

        # добавляем новую монету вместо собранной
        coins.add(Coin())

    # движение игрока и врага
    for entity in all_sprites:
        entity.move()
        DISPLAYSURF.blit(entity.image, entity.rect)

    # проверка столкновения с врагом
    if pygame.sprite.spritecollideany(P1, enemies):
        try:
            crash_sound = pygame.mixer.Sound(ASSETS / "crash.wav")
            crash_sound.play()
        except Exception:
            pass

        time.sleep(0.5)

        # экран проигрыша
        DISPLAYSURF.fill(RED)
        DISPLAYSURF.blit(game_over_surf, (35, 190))

        # финальная статистика
        lines = [
            f"Score: {SCORE}",
            f"Coins collected: {TOTAL_COINS}",
            f"Enemy boosts earned: {ENEMY_BOOSTS}",
        ]

        # вывод статистики
        for i, line in enumerate(lines):
            surf = font_small.render(line, True, WHITE)
            DISPLAYSURF.blit(surf, (75, 290 + i * 30))

        pygame.display.update()
        time.sleep(2)

        pygame.quit()
        sys.exit()

    # обновление экрана
    pygame.display.update()

    # ограничение FPS
    FramePerSec.tick(FPS)