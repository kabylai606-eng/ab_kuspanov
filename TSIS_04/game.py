import array
import math
import random
import pygame
from config import (CELL_SIZE, GRID_COLS, GRID_ROWS, HUD_HEIGHT,
                    WINDOW_WIDTH, WINDOW_HEIGHT, BASE_SPEED,
                    FOODS_PER_LEVEL, FOOD_LIFETIME_MS,
                    POWERUP_LIFETIME_MS, POWERUP_EFFECT_MS, OBSTACLE_COUNT)


def cell_to_px(x, y):
    return x * CELL_SIZE, HUD_HEIGHT + y * CELL_SIZE


def is_wall(cell):
    x, y = cell
    return x == 0 or y == 0 or x == GRID_COLS - 1 or y == GRID_ROWS - 1


def is_opposite(a, b):
    return a[0] == -b[0] and a[1] == -b[1]


def free_cells(blocked):
    # All interior cells not in the blocked set
    cells = []
    for x in range(1, GRID_COLS - 1):
        for y in range(1, GRID_ROWS - 1):
            if (x, y) not in blocked:
                cells.append((x, y))
    return cells


def snake_is_trapped(head, obstacles, snake):
    # BFS from head — if fewer than 8 reachable cells the snake is trapped
    blocked = set(obstacles) | set(snake)
    visited = {head}
    queue   = [head]
    while queue:
        if len(visited) >= 8:
            return False
        x, y = queue.pop(0)
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nb = (x + dx, y + dy)
            if (nb not in blocked and nb not in visited
                    and 0 < nb[0] < GRID_COLS - 1 and 0 < nb[1] < GRID_ROWS - 1):
                visited.add(nb)
                queue.append(nb)
    return len(visited) < 8


def _gen_tone(freq, ms, vol=0.4, rate=44100):
    n = int(rate * ms / 1000)
    buf = array.array('h', [0] * n)
    for i in range(n):
        buf[i] = int(vol * 32767 * math.sin(2 * math.pi * freq * i / rate))
    return pygame.mixer.Sound(buffer=buf)


def make_sounds():
    return {
        "eat":      _gen_tone(660, 80),
        "poison":   _gen_tone(200, 300, vol=0.5),
        "powerup":  _gen_tone(880, 150),
        "gameover": _gen_tone(160, 500, vol=0.6),
    }


class SnakeGame:
    def __init__(self, screen, settings, username, personal_best, db_available):
        self.screen        = screen
        self.username      = username
        self.personal_best = personal_best
        self.db_available  = db_available

        self.snake_color  = tuple(settings.get("snake_color", [45, 185, 70]))
        self.grid_overlay = settings.get("grid_overlay", True)
        self.sound_on     = settings.get("sound", False)
        self.sounds       = make_sounds() if self.sound_on else {}

        self.hud_font  = pygame.font.SysFont("arial", 22, bold=True)
        self.info_font = pygame.font.SysFont("arial", 17)
        self.food_font = pygame.font.SysFont("arial", 15, bold=True)
        self.clock     = pygame.time.Clock()

        self.reset()

    def _play(self, name):
        if self.sound_on and name in self.sounds:
            self.sounds[name].play()

    def reset(self):
        sx, sy = GRID_COLS // 2, GRID_ROWS // 2
        self.snake         = [(sx, sy), (sx - 1, sy), (sx - 2, sy)]
        self.direction     = (1, 0)
        self.next_dir      = (1, 0)
        self.score         = 0
        self.level         = 1
        self.speed         = BASE_SPEED
        self.obstacles     = set()
        self.poison        = None

        self.food          = self._make_food()
        self.poison_timer  = pygame.time.get_ticks() + random.randint(5000, 10000)

        # Power-up on the field (only one at a time)
        self.field_powerup = None   # {"pos", "kind", "spawn_time"}
        self.pu_spawn_time = pygame.time.get_ticks() + random.randint(8000, 15000)

        # Active power-up effect
        self.active_pu     = None   # "speed_boost" | "slow_motion" | "shield"
        self.pu_end_time   = 0

        self.shield_ready  = False  # shield lasts until one collision
        self.game_over     = False

    # -------------------------------------------------------------------------
    # Food / poison / power-up generation
    # -------------------------------------------------------------------------

    def _blocked_cells(self):
        return set(self.snake) | self.obstacles

    def _make_food(self):
        blocked = self._blocked_cells()
        if self.poison:
            blocked.add(self.poison["pos"])
        candidates = free_cells(blocked)
        pos = random.choice(candidates) if candidates else (1, 1)
        weight, color = random.choice([
            (1, (230, 70,  70)),
            (2, (255, 170, 40)),
            (3, (180, 80, 255)),
        ])
        return {"pos": pos, "weight": weight, "color": color,
                "spawn_time": pygame.time.get_ticks()}

    def _make_poison(self):
        blocked = self._blocked_cells() | {self.food["pos"]}
        candidates = free_cells(blocked)
        if not candidates:
            return None
        return {"pos": random.choice(candidates),
                "spawn_time": pygame.time.get_ticks()}

    def _make_field_powerup(self):
        blocked = self._blocked_cells() | {self.food["pos"]}
        if self.poison:
            blocked.add(self.poison["pos"])
        candidates = free_cells(blocked)
        if not candidates:
            return None
        kind = random.choice(["speed_boost", "slow_motion", "shield"])
        return {"pos": random.choice(candidates), "kind": kind,
                "spawn_time": pygame.time.get_ticks()}

    def _make_obstacles(self):
        # Place OBSTACLE_COUNT random blocks, retry until snake is not trapped
        blocked_base = set(self.snake) | {self.food["pos"]}
        candidates   = free_cells(blocked_base)
        obs = set()
        for _ in range(OBSTACLE_COUNT):
            if not candidates:
                break
            cell = random.choice(candidates)
            trial = obs | {cell}
            if not snake_is_trapped(self.snake[0], trial, self.snake):
                obs.add(cell)
                candidates.remove(cell)
        self.obstacles = obs

    # -------------------------------------------------------------------------
    # Level / speed
    # -------------------------------------------------------------------------

    def _update_level(self):
        new_level = 1 + self.score // FOODS_PER_LEVEL
        if new_level != self.level:
            self.level = new_level
            self.speed = BASE_SPEED + (self.level - 1) * 2
            if self.level >= 3:
                self._make_obstacles()

    # -------------------------------------------------------------------------
    # Active power-up helpers
    # -------------------------------------------------------------------------

    def _apply_powerup(self, kind):
        now = pygame.time.get_ticks()
        self.active_pu   = kind
        self.pu_end_time = now + POWERUP_EFFECT_MS
        if kind == "speed_boost":
            self.speed = min(self.speed + 4, BASE_SPEED + 20)
        elif kind == "slow_motion":
            self.speed = max(1, self.speed - 3)
        elif kind == "shield":
            self.shield_ready = True
            self.active_pu    = None  # shield has no timed expiry

    def _check_powerup_expiry(self):
        if self.active_pu in ("speed_boost", "slow_motion"):
            if pygame.time.get_ticks() >= self.pu_end_time:
                # Revert speed to what it should be for the current level
                self.speed    = BASE_SPEED + (self.level - 1) * 2
                self.active_pu = None

    # -------------------------------------------------------------------------
    # Main update
    # -------------------------------------------------------------------------

    def update(self):
        if self.game_over:
            return

        now = pygame.time.get_ticks()

        # Rotate food if timer expired
        if now - self.food["spawn_time"] >= FOOD_LIFETIME_MS:
            self.food = self._make_food()

        # Spawn poison food after its random delay
        if self.poison is None and now >= self.poison_timer:
            self.poison = self._make_poison()

        # Remove poison if it has been on the field too long
        if self.poison and now - self.poison["spawn_time"] >= FOOD_LIFETIME_MS:
            self.poison = None
            self.poison_timer = now + random.randint(5000, 10000)

        # Spawn a field power-up if none is on the field
        if self.field_powerup is None and now >= self.pu_spawn_time:
            self.field_powerup = self._make_field_powerup()

        # Expire field power-up if not collected in time
        if self.field_powerup and now - self.field_powerup["spawn_time"] >= POWERUP_LIFETIME_MS:
            self.field_powerup = None
            self.pu_spawn_time = now + random.randint(8000, 15000)

        self._check_powerup_expiry()

        # Move snake
        self.direction = self.next_dir
        hx, hy = self.snake[0]
        dx, dy  = self.direction
        new_head = (hx + dx, hy + dy)

        # Collision with wall or self
        if is_wall(new_head) or new_head in self.snake or new_head in self.obstacles:
            if self.shield_ready:
                # Shield absorbs the collision; snake stays put this tick
                self.shield_ready = False
                return
            self._play("gameover")
            self.game_over = True
            return

        self.snake.insert(0, new_head)

        # Eat normal food
        if new_head == self.food["pos"]:
            self._play("eat")
            self.score += self.food["weight"]
            self._update_level()
            self.food = self._make_food()
        # Eat poison
        elif self.poison and new_head == self.poison["pos"]:
            self._play("poison")
            self.poison = None
            self.poison_timer = now + random.randint(5000, 10000)
            # Shrink snake by 2; game over if too short
            for _ in range(2):
                if len(self.snake) > 1:
                    self.snake.pop()
            if len(self.snake) <= 1:
                self._play("gameover")
                self.game_over = True
                return
        # Collect power-up
        elif self.field_powerup and new_head == self.field_powerup["pos"]:
            self._play("powerup")
            self._apply_powerup(self.field_powerup["kind"])
            self.field_powerup = None
            self.pu_spawn_time = now + random.randint(8000, 15000)
        else:
            self.snake.pop()

    # -------------------------------------------------------------------------
    # Drawing
    # -------------------------------------------------------------------------

    def _draw_hud(self):
        pygame.draw.rect(self.screen, (30, 30, 38), (0, 0, WINDOW_WIDTH, HUD_HEIGHT))

        self.screen.blit(self.hud_font.render("SNAKE", True, (240, 240, 240)), (12, 12))

        score_s = self.hud_font.render(f"Score: {self.score}", True, (245, 245, 245))
        level_s = self.hud_font.render(f"Level: {self.level}", True, (245, 245, 245))
        self.screen.blit(score_s, (160, 12))
        self.screen.blit(level_s, (340, 12))

        pb_s = self.info_font.render(f"Best: {self.personal_best}", True, (255, 200, 40))
        self.screen.blit(pb_s, (490, 12))

        # Food timer
        elapsed = pygame.time.get_ticks() - self.food["spawn_time"]
        secs    = max(0.0, (FOOD_LIFETIME_MS - elapsed) / 1000)
        ft_s    = self.info_font.render(f"Food: {secs:.1f}s", True, (255, 215, 128))
        self.screen.blit(ft_s, (160, 38))

        # Active power-up indicator
        if self.active_pu:
            rem  = max(0, self.pu_end_time - pygame.time.get_ticks()) // 1000
            color = (30, 160, 240) if self.active_pu == "speed_boost" else (240, 160, 30)
            pu_s = self.info_font.render(f"{self.active_pu.upper()} {rem}s", True, color)
            self.screen.blit(pu_s, (340, 38))
        elif self.shield_ready:
            self.screen.blit(self.info_font.render("SHIELD", True, (60, 210, 100)), (340, 38))

    def _draw_grid(self):
        play_area = pygame.Rect(0, HUD_HEIGHT, WINDOW_WIDTH, WINDOW_HEIGHT - HUD_HEIGHT)
        pygame.draw.rect(self.screen, (18, 18, 20), play_area)

        # Border walls
        for x in range(GRID_COLS):
            for y in range(GRID_ROWS):
                if is_wall((x, y)):
                    px, py = cell_to_px(x, y)
                    pygame.draw.rect(self.screen, (80, 80, 90),
                                     (px, py, CELL_SIZE, CELL_SIZE))

        # Optional grid lines
        if self.grid_overlay:
            for x in range(1, GRID_COLS - 1):
                for y in range(1, GRID_ROWS - 1):
                    px, py = cell_to_px(x, y)
                    pygame.draw.rect(self.screen, (28, 28, 32),
                                     (px, py, CELL_SIZE, CELL_SIZE), 1)

    def _draw_obstacles(self):
        for (x, y) in self.obstacles:
            px, py = cell_to_px(x, y)
            pygame.draw.rect(self.screen, (100, 100, 110),
                             (px + 2, py + 2, CELL_SIZE - 4, CELL_SIZE - 4), border_radius=3)

    def _draw_food(self):
        fx, fy = self.food["pos"]
        cx, cy = fx * CELL_SIZE + CELL_SIZE // 2, HUD_HEIGHT + fy * CELL_SIZE + CELL_SIZE // 2
        pygame.draw.circle(self.screen, self.food["color"], (cx, cy), CELL_SIZE // 2 - 3)
        lbl = self.food_font.render(str(self.food["weight"]), True, (255, 255, 255))
        self.screen.blit(lbl, lbl.get_rect(center=(cx, cy)))

    def _draw_poison(self):
        if not self.poison:
            return
        fx, fy = self.poison["pos"]
        cx = fx * CELL_SIZE + CELL_SIZE // 2
        cy = HUD_HEIGHT + fy * CELL_SIZE + CELL_SIZE // 2
        pygame.draw.circle(self.screen, (130, 10, 10), (cx, cy), CELL_SIZE // 2 - 3)
        pygame.draw.circle(self.screen, (80, 0, 0), (cx, cy), CELL_SIZE // 2 - 3, 2)
        lbl = self.food_font.render("☠", True, (220, 80, 80))
        self.screen.blit(lbl, lbl.get_rect(center=(cx, cy)))

    def _draw_field_powerup(self):
        if not self.field_powerup:
            return
        px, py = self.field_powerup["pos"]
        kind   = self.field_powerup["kind"]
        color  = {"speed_boost": (30, 180, 240),
                  "slow_motion": (240, 160, 30),
                  "shield":      (60, 210, 100)}[kind]
        letter = {"speed_boost": "F", "slow_motion": "S", "shield": "Sh"}[kind]
        cx = px * CELL_SIZE + CELL_SIZE // 2
        cy = HUD_HEIGHT + py * CELL_SIZE + CELL_SIZE // 2
        pygame.draw.circle(self.screen, color, (cx, cy), CELL_SIZE // 2 - 2)
        pygame.draw.circle(self.screen, (255, 255, 255), (cx, cy), CELL_SIZE // 2 - 2, 2)
        lbl = self.food_font.render(letter, True, (255, 255, 255))
        self.screen.blit(lbl, lbl.get_rect(center=(cx, cy)))

    def _draw_snake(self):
        head_color = tuple(min(255, c + 50) for c in self.snake_color)
        for i, (x, y) in enumerate(self.snake):
            px, py = cell_to_px(x, y)
            color  = head_color if i == 0 else self.snake_color
            pygame.draw.rect(self.screen, color,
                             (px + 2, py + 2, CELL_SIZE - 4, CELL_SIZE - 4), border_radius=5)

    def draw(self):
        self.screen.fill((0, 0, 0))
        self._draw_hud()
        self._draw_grid()
        self._draw_obstacles()
        self._draw_food()
        self._draw_poison()
        self._draw_field_powerup()
        self._draw_snake()

    # -------------------------------------------------------------------------
    # Main loop — returns {"score": int, "level": int}
    # -------------------------------------------------------------------------

    def run(self):
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False

                    if not self.game_over:
                        wanted = self.next_dir
                        if event.key == pygame.K_LEFT:
                            wanted = (-1, 0)
                        elif event.key == pygame.K_RIGHT:
                            wanted = (1, 0)
                        elif event.key == pygame.K_UP:
                            wanted = (0, -1)
                        elif event.key == pygame.K_DOWN:
                            wanted = (0, 1)
                        if not is_opposite(wanted, self.direction):
                            self.next_dir = wanted

            if not self.game_over:
                self.update()

            self.draw()

            if self.game_over:
                overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 140))
                self.screen.blit(overlay, (0, 0))
                font = pygame.font.SysFont("arial", 32, bold=True)
                msg  = font.render("GAME OVER — returning to menu", True, (255, 255, 255))
                self.screen.blit(msg, msg.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)))

            pygame.display.flip()

            if self.game_over:
                pygame.time.wait(1800)
                running = False
            else:
                self.clock.tick(self.speed)

        return {"score": self.score, "level": self.level}