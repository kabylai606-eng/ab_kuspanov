import pygame
import sys
import random
import time as pytime
import math
from pygame.locals import *

pygame.init()  # запуск pygame

# размеры клетки и поля
CELL = 20
COLS = 30
ROWS = 30
WIDTH = COLS * CELL
HEIGHT = ROWS * CELL

# сколько еды нужно для нового уровня
FOODS_PER_LEVEL = 4

# направления движения
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# основные цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (50, 200, 50)
DARK_GREEN = (30, 130, 30)
GRAY = (40, 40, 40)
WALL_COLOR = (80, 80, 80)
GOLD = (255, 215, 0)

# цвета еды
COMMON_COLOR = (220, 50, 50)
RARE_COLOR = (50, 100, 255)
LEGENDARY_COLOR = (220, 180, 0)

# типы еды
FOOD_TIERS = [
    {"name": "Common", "pts": 10, "color": COMMON_COLOR, "weight": 60, "timeout": 10},
    {"name": "Rare", "pts": 30, "color": RARE_COLOR, "weight": 30, "timeout": 7},
    {"name": "Legendary", "pts": 50, "color": LEGENDARY_COLOR, "weight": 10, "timeout": 4},
]


# выбор случайного типа еды
def pick_food_tier():
    total = sum(tier["weight"] for tier in FOOD_TIERS)
    rnd = random.randint(1, total)
    current = 0

    for tier in FOOD_TIERS:
        current += tier["weight"]
        if rnd <= current:
            return tier

    return FOOD_TIERS[0]


# создание окна
DISPLAYSURF = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake – Practice 11")

# шрифты
font_hud = pygame.font.SysFont("Verdana", 18)
font_small = pygame.font.SysFont("Verdana", 14)
font_big = pygame.font.SysFont("Verdana", 48)


# проверка стены
def is_wall(col, row):
    return col == 0 or row == 0 or col == COLS - 1 or row == ROWS - 1


# случайная позиция еды
def random_food_position(snake_body, excluded=None):
    excluded = excluded or set()

    while True:
        col = random.randint(1, COLS - 2)
        row = random.randint(1, ROWS - 2)

        if (col, row) not in snake_body and (col, row) not in excluded:
            return col, row


# рисует игровую сетку
def draw_grid():
    for col in range(COLS):
        for row in range(ROWS):
            rect = pygame.Rect(col * CELL, row * CELL, CELL, CELL)

            # стены рисуются другим цветом
            if is_wall(col, row):
                pygame.draw.rect(DISPLAYSURF, WALL_COLOR, rect)
            else:
                pygame.draw.rect(DISPLAYSURF, GRAY, rect)

            # контур клетки
            pygame.draw.rect(DISPLAYSURF, BLACK, rect, 1)


# рисует змейку
def draw_snake(snake):
    for index, (col, row) in enumerate(snake):
        # голова темнее, тело светлее
        color = DARK_GREEN if index == 0 else GREEN

        rect = pygame.Rect(
            col * CELL + 1,
            row * CELL + 1,
            CELL - 2,
            CELL - 2
        )

        pygame.draw.rect(DISPLAYSURF, color, rect)


# рисует всю еду
def draw_food_items(food_items, now):
    for item in food_items:
        col, row = item["pos"]
        tier = item["tier"]

        # оставшееся время еды
        elapsed = now - item["spawn_time"]
        remaining = max(0, tier["timeout"] - elapsed)

        # центр клетки
        cx = col * CELL + CELL // 2
        cy = row * CELL + CELL // 2

        # рисует круг еды
        pygame.draw.circle(
            DISPLAYSURF,
            tier["color"],
            (cx, cy),
            CELL // 2 - 1
        )

        # рисует таймер вокруг еды
        if remaining > 0:
            fraction = remaining / tier["timeout"]
            arc_rect = pygame.Rect(col * CELL, row * CELL, CELL, CELL)
            end_angle = 2 * math.pi * fraction

            pygame.draw.arc(
                DISPLAYSURF,
                WHITE,
                arc_rect,
                0,
                end_angle,
                2
            )

        # показывает очки еды
        pts_surf = font_small.render(f"+{tier['pts']}", True, WHITE)
        DISPLAYSURF.blit(
            pts_surf,
            pts_surf.get_rect(center=(cx, cy))
        )


# рисует информацию сверху и снизу
def draw_hud(score, level, foods_eaten, total_foods_for_level):
    # score
    score_text = font_hud.render(f"Score: {score}", True, WHITE)
    DISPLAYSURF.blit(score_text, (CELL + 5, 5))

    # level
    level_text = font_hud.render(f"Level: {level}", True, GOLD)
    DISPLAYSURF.blit(level_text, (CELL + 5, 28))

    # сколько осталось до нового уровня
    next_text = f"Next lvl: {total_foods_for_level - foods_eaten} food"
    next_surf = font_hud.render(next_text, True, WHITE)
    DISPLAYSURF.blit(next_surf, (WIDTH - 220, 5))

    # легенда еды
    legend_y = HEIGHT - 70

    for tier in FOOD_TIERS:
        pygame.draw.circle(
            DISPLAYSURF,
            tier["color"],
            (CELL + 10, legend_y),
            7
        )

        label = font_small.render(
            f"{tier['name']}: +{tier['pts']} pts ({tier['timeout']}s)",
            True,
            WHITE
        )

        DISPLAYSURF.blit(label, (CELL + 22, legend_y - 8))
        legend_y += 22


# экран окончания игры
def game_over_screen(score, level):
    # полупрозрачный фон
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    DISPLAYSURF.blit(overlay, (0, 0))

    # текст Game Over
    game_over_text = font_big.render("GAME OVER", True, (220, 50, 50))
    DISPLAYSURF.blit(
        game_over_text,
        game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 60))
    )

    # финальный score и level
    score_text = font_hud.render(f"Score: {score}   Level: {level}", True, WHITE)
    DISPLAYSURF.blit(
        score_text,
        score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    )

    # инструкция выхода
    quit_text = font_hud.render("Press any key to quit", True, WHITE)
    DISPLAYSURF.blit(
        quit_text,
        quit_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
    )

    pygame.display.update()

    # ждет нажатия клавиши или закрытия окна
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            if event.type == KEYDOWN:
                waiting = False


# начальное состояние змейки
snake = [
    (COLS // 2, ROWS // 2),
    (COLS // 2 - 1, ROWS // 2),
    (COLS // 2 - 2, ROWS // 2)
]

# начальное направление
direction = RIGHT
next_direction = RIGHT

# игровые значения
score = 0
level = 1
foods_eaten = 0

# скорость движения змейки
BASE_SPEED_MS = 200

# событие движения
MOVE_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(MOVE_EVENT, BASE_SPEED_MS)

# список еды на поле
food_items = []


# добавляет новую еду
def add_food_item(snake_body, existing_food):
    excluded = {item["pos"] for item in existing_food}
    pos = random_food_position(snake_body, excluded)

    food_items.append({
        "pos": pos,
        "tier": pick_food_tier(),
        "spawn_time": pytime.time(),
    })


# начальная еда
add_food_item(snake, food_items)
add_food_item(snake, food_items)

# FPS
clock = pygame.time.Clock()

# флаг работы игры
running = True


# главный игровой цикл
while running:
    clock.tick(60)

    # текущее время
    now = pytime.time()

    # удаляет еду, если время закончилось
    active_food = []

    for item in food_items:
        if now - item["spawn_time"] < item["tier"]["timeout"]:
            active_food.append(item)

    food_items = active_food

    # если еды нет, добавляем новую
    if len(food_items) == 0:
        add_food_item(snake, food_items)

    # обработка событий
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

        # управление стрелками
        if event.type == KEYDOWN:
            if event.key == K_UP and direction != DOWN:
                next_direction = UP

            elif event.key == K_DOWN and direction != UP:
                next_direction = DOWN

            elif event.key == K_LEFT and direction != RIGHT:
                next_direction = LEFT

            elif event.key == K_RIGHT and direction != LEFT:
                next_direction = RIGHT

        # движение змейки по таймеру
        if event.type == MOVE_EVENT:
            direction = next_direction

            head_col, head_row = snake[0]
            move_col, move_row = direction

            new_head = (
                head_col + move_col,
                head_row + move_row
            )

            # столкновение со стеной
            if is_wall(*new_head):
                game_over_screen(score, level)
                running = False
                break

            # столкновение с собой
            if new_head in snake[1:]:
                game_over_screen(score, level)
                running = False
                break

            # добавляем новую голову
            snake.insert(0, new_head)

            # проверка съеденной еды
            ate_food = False

            for item in food_items[:]:
                if new_head == item["pos"]:
                    # начисляем очки
                    score += item["tier"]["pts"] * level
                    foods_eaten += 1
                    ate_food = True

                    # убираем съеденную еду
                    food_items.remove(item)

                    # добавляем новую еду
                    add_food_item(snake, food_items)

                    # проверка перехода уровня
                    if foods_eaten >= FOODS_PER_LEVEL:
                        level += 1
                        foods_eaten = 0

                        # ускорение змейки
                        new_delay = max(
                            60,
                            BASE_SPEED_MS - (level - 1) * 25
                        )

                        pygame.time.set_timer(MOVE_EVENT, new_delay)

                        # больше еды на высоких уровнях
                        if len(food_items) < level + 1:
                            add_food_item(snake, food_items)

                    break

            # если еда не съедена — удаляем хвост
            if not ate_food:
                snake.pop()

    # если игра закончилась
    if not running:
        break

    # рисование всех элементов
    draw_grid()
    draw_food_items(food_items, now)
    draw_snake(snake)
    draw_hud(score, level, foods_eaten, FOODS_PER_LEVEL)

    # обновление экрана
    pygame.display.update()

# закрытие pygame
pygame.quit()
sys.exit()