import array
import math
import random
import pygame

WINDOW_WIDTH  = 420
WINDOW_HEIGHT = 700
ROAD_LEFT     = 70
ROAD_RIGHT    = 350
ROAD_WIDTH    = ROAD_RIGHT - ROAD_LEFT   # 280
LANE_COUNT    = 3
LANE_WIDTH    = ROAD_WIDTH // LANE_COUNT  # 93
LANE_CENTERS  = [ROAD_LEFT + LANE_WIDTH // 2 + i * LANE_WIDTH for i in range(LANE_COUNT)]
FPS           = 60

PLAYER_SIZE = (56, 96)
ENEMY_SIZE  = (56, 88)
COIN_SIZE   = (30, 30)

CAR_COLORS = {
    "blue":   (40, 120, 255),
    "red":    (225, 64,  64),
    "green":  (50, 200,  80),
    "yellow": (255, 210,  30),
}

DIFF_CONFIG = {
    "easy":   {"enemies": 1, "speed": 4, "obs_chance": 0.25, "spawn_ms": 2000, "race_m": 3000},
    "medium": {"enemies": 2, "speed": 5, "obs_chance": 0.45, "spawn_ms": 1400, "race_m": 5000},
    "hard":   {"enemies": 3, "speed": 6, "obs_chance": 0.65, "spawn_ms": 950,  "race_m": 8000},
}

POWERUP_COLORS   = {"nitro": (30, 160, 240), "shield": (60, 210, 100), "repair": (255, 200, 40)}
POWERUP_LETTERS  = {"nitro": "N", "shield": "S", "repair": "R"}
NITRO_FRAMES     = 4 * FPS
POWERUP_EXPIRE   = 6 * FPS
OIL_SLOW_FRAMES  = 2 * FPS


# ---------------------------------------------------------------------------
# Programmatic art helpers
# ---------------------------------------------------------------------------

def make_car(size, color):
    w, h = size
    surf = pygame.Surface(size, pygame.SRCALPHA)
    pygame.draw.rect(surf, color, (6, 10, w - 12, h - 20), border_radius=14)
    pygame.draw.rect(surf, (220, 235, 245), (12, 18, w - 24, 24), border_radius=8)
    for ty in (18, h - 40):
        pygame.draw.rect(surf, (20, 20, 20), (2, ty, 6, 22), border_radius=3)
        pygame.draw.rect(surf, (20, 20, 20), (w - 8, ty, 6, 22), border_radius=3)
    return surf


def make_coin():
    surf = pygame.Surface(COIN_SIZE, pygame.SRCALPHA)
    cx, cy = COIN_SIZE[0] // 2, COIN_SIZE[1] // 2
    r = min(COIN_SIZE) // 2 - 2
    pygame.draw.circle(surf, (245, 199, 45), (cx, cy), r)
    pygame.draw.circle(surf, (255, 235, 120), (cx, cy), r - 5)
    pygame.draw.circle(surf, (210, 150, 25), (cx, cy), r, 2)
    return surf


def make_road():
    surf = pygame.Surface((ROAD_WIDTH, WINDOW_HEIGHT))
    surf.fill((48, 48, 54))
    for lx in (LANE_WIDTH, LANE_WIDTH * 2):
        for y in range(0, WINDOW_HEIGHT, 90):
            pygame.draw.rect(surf, (245, 245, 245), (lx - 3, y, 6, 52), border_radius=2)
    pygame.draw.rect(surf, (230, 220, 80), (0, 0, 6, WINDOW_HEIGHT))
    pygame.draw.rect(surf, (230, 220, 80), (ROAD_WIDTH - 6, 0, 6, WINDOW_HEIGHT))
    return surf


def make_barrier():
    w, h = LANE_WIDTH - 14, 28
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(surf, (230, 70, 30), (0, 0, w, h), border_radius=6)
    for i in range(0, w, 20):
        pygame.draw.rect(surf, (240, 230, 50), (i, 0, 10, h), border_radius=3)
    return surf


def make_oil():
    surf = pygame.Surface((46, 28), pygame.SRCALPHA)
    pygame.draw.ellipse(surf, (20, 18, 30, 200), (0, 4, 46, 20))
    pygame.draw.ellipse(surf, (70, 55, 100, 170), (6, 8, 34, 12))
    return surf


def make_pothole():
    surf = pygame.Surface((42, 24), pygame.SRCALPHA)
    pygame.draw.ellipse(surf, (30, 28, 22), (0, 0, 42, 24))
    pygame.draw.ellipse(surf, (50, 45, 35), (4, 4, 34, 16))
    return surf


def make_powerup_sprite(kind):
    surf = pygame.Surface((36, 36), pygame.SRCALPHA)
    color = POWERUP_COLORS[kind]
    pygame.draw.circle(surf, color, (18, 18), 16)
    pygame.draw.circle(surf, (255, 255, 255), (18, 18), 16, 2)
    font = pygame.font.SysFont("arial", 18, bold=True)
    lbl = font.render(POWERUP_LETTERS[kind], True, (255, 255, 255))
    surf.blit(lbl, lbl.get_rect(center=(18, 18)))
    return surf


def make_road_strip(kind):
    color = (0, 210, 240, 160) if kind == "nitro" else (255, 145, 0, 160)
    surf = pygame.Surface((ROAD_WIDTH, 22), pygame.SRCALPHA)
    surf.fill(color)
    font = pygame.font.SysFont("arial", 13, bold=True)
    label = "NITRO STRIP" if kind == "nitro" else "SPEED BUMP"
    lbl = font.render(label, True, (255, 255, 255))
    surf.blit(lbl, lbl.get_rect(center=(ROAD_WIDTH // 2, 11)))
    return surf


# ---------------------------------------------------------------------------
# Sound helpers
# ---------------------------------------------------------------------------

def _gen_tone(freq, ms, vol=0.4, rate=44100):
    n = int(rate * ms / 1000)
    buf = array.array('h', [0] * n)
    for i in range(n):
        buf[i] = int(vol * 32767 * math.sin(2 * math.pi * freq * i / rate))
    return pygame.mixer.Sound(buffer=buf)


def make_sounds():
    return {
        "coin":    _gen_tone(880, 80),
        "powerup": _gen_tone(660, 200),
        "crash":   _gen_tone(180, 400, vol=0.6),
    }


# ---------------------------------------------------------------------------
# Sprite classes
# ---------------------------------------------------------------------------

class Player(pygame.sprite.Sprite):
    def __init__(self, car_color_name):
        super().__init__()
        color = CAR_COLORS.get(car_color_name, CAR_COLORS["blue"])
        self.image = make_car(PLAYER_SIZE, color)
        self.rect  = self.image.get_rect(midbottom=(LANE_CENTERS[1], WINDOW_HEIGHT - 22))
        self.lane  = 1

        self.active_powerup = None  # "nitro" or "shield"
        self.powerup_frames = 0
        self.slow_frames    = 0

    def move_left(self):
        if self.lane > 0:
            self.lane -= 1
            self.rect.centerx = LANE_CENTERS[self.lane]

    def move_right(self):
        if self.lane < LANE_COUNT - 1:
            self.lane += 1
            self.rect.centerx = LANE_CENTERS[self.lane]

    def apply_powerup(self, kind):
        if kind == "repair":
            self.slow_frames = 0
            return
        self.active_powerup = kind
        self.powerup_frames = NITRO_FRAMES if kind == "nitro" else 0

    def tick(self):
        if self.active_powerup == "nitro":
            self.powerup_frames -= 1
            if self.powerup_frames <= 0:
                self.active_powerup = None
        if self.slow_frames > 0:
            self.slow_frames -= 1

    @property
    def has_shield(self):
        return self.active_powerup == "shield"

    def consume_shield(self):
        self.active_powerup = None


class Enemy(pygame.sprite.Sprite):
    def __init__(self, speed):
        super().__init__()
        self.image = make_car(ENEMY_SIZE, (225, 64, 64))
        self.rect  = self.image.get_rect()
        self.speed = speed

        # Initial temporary position. RacerGame will place enemies safely.
        self.rect.centerx = random.choice(LANE_CENTERS)
        self.rect.y = random.randint(-700, -120)

    def update(self, speed):
        self.speed = speed
        self.rect.y += self.speed


class Coin(pygame.sprite.Sprite):
    def __init__(self, base_img, speed, weight, wfont):
        super().__init__()
        self.weight = weight
        scale = {1: 0.85, 2: 1.0, 3: 1.2}[weight]
        w = max(18, int(base_img.get_width() * scale))
        h = max(18, int(base_img.get_height() * scale))
        self.image = pygame.transform.smoothscale(base_img, (w, h))
        self.rect  = self.image.get_rect()
        self.rect.centerx = random.choice(LANE_CENTERS)
        self.rect.y = random.randint(-600, -80)
        self.speed = speed
        self.label = wfont.render(str(weight), True, (35, 35, 35))

    def update(self, speed):
        self.speed = speed
        self.rect.y += self.speed
        if self.rect.top > WINDOW_HEIGHT:
            self.kill()

    def draw_label(self, screen):
        screen.blit(self.label, self.label.get_rect(center=self.rect.center))


class Obstacle(pygame.sprite.Sprite):
    def __init__(self, kind, speed):
        super().__init__()
        self.kind  = kind
        self.image = {"barrier": make_barrier, "oil": make_oil, "pothole": make_pothole}[kind]()
        self.rect  = self.image.get_rect()
        self.rect.centerx = random.choice(LANE_CENTERS)
        self.rect.y = -self.rect.height - 10
        self.speed = speed

    def update(self, speed):
        self.rect.y += speed
        if self.rect.top > WINDOW_HEIGHT:
            self.kill()


class PowerUp(pygame.sprite.Sprite):
    def __init__(self, kind, speed):
        super().__init__()
        self.kind   = kind
        self.image  = make_powerup_sprite(kind)
        self.rect   = self.image.get_rect()
        self.rect.centerx = random.choice(LANE_CENTERS)
        self.rect.y = -40
        self.speed  = speed
        self.frames_left = POWERUP_EXPIRE

    def update(self, speed):
        self.rect.y += speed
        self.frames_left -= 1
        if self.rect.top > WINDOW_HEIGHT or self.frames_left <= 0:
            self.kill()


class RoadStrip(pygame.sprite.Sprite):
    def __init__(self, kind, speed):
        super().__init__()
        self.kind  = kind
        self.image = make_road_strip(kind)
        self.rect  = self.image.get_rect()
        self.rect.x = ROAD_LEFT
        self.rect.y = -25
        self.speed  = speed

    def update(self, speed):
        self.rect.y += speed
        if self.rect.top > WINDOW_HEIGHT:
            self.kill()


def is_lane_clear(lane_center, sprites, min_gap=150):
    """
    Returns False if another sprite is too close in the same lane.
    This prevents coins, power-ups and obstacles from spawning on top
    of cars or each other, but still allows objects far apart.
    """
    spawn_y = -80
    for s in sprites:
        same_lane = abs(s.rect.centerx - lane_center) < LANE_WIDTH // 2
        if not same_lane:
            continue

        near_spawn_area = s.rect.bottom > -220 and s.rect.top < WINDOW_HEIGHT * 0.55
        close_vertically = abs(s.rect.centery - spawn_y) < min_gap

        if near_spawn_area or close_vertically:
            return False
    return True


def is_coin_lane_safe(lane_center, enemies, obstacles):
    """
    Coins and power-ups are rewards, so they must not appear in a lane
    that is currently occupied by a dangerous object: enemy car or barrier.
    """
    for enemy in enemies:
        if abs(enemy.rect.centerx - lane_center) < LANE_WIDTH // 2:
            if enemy.rect.bottom > -220 and enemy.rect.top < WINDOW_HEIGHT:
                return False

    for obs in obstacles:
        if getattr(obs, "kind", None) != "barrier":
            continue
        if abs(obs.rect.centerx - lane_center) < LANE_WIDTH // 2:
            if obs.rect.bottom > -220 and obs.rect.top < WINDOW_HEIGHT:
                return False

    return True

def enemy_lane_index(enemy):
    """Returns the lane number where an enemy car is located."""
    return min(range(LANE_COUNT), key=lambda i: abs(enemy.rect.centerx - LANE_CENTERS[i]))


def sprite_lane_index(sprite):
    """Returns the lane number where a sprite is located."""
    return min(range(LANE_COUNT), key=lambda i: abs(sprite.rect.centerx - LANE_CENTERS[i]))


def occupied_enemy_lanes(enemies):
    """
    Returns lanes that are already dangerous because enemy cars are visible
    or are close to entering the screen.

    The important gameplay rule is this:
    if enemies already occupy 2 different lanes, a new enemy must NOT appear
    in the 3rd free lane. This always leaves the player one escape lane.
    """
    lanes = set()
    for enemy in enemies:
        if enemy.rect.bottom > -180 and enemy.rect.top < WINDOW_HEIGHT:
            lanes.add(enemy_lane_index(enemy))
    return lanes


def occupied_blocker_lanes(enemies, obstacles=None, ignore_sprite=None):
    """
    Returns lanes that are blocked by dangerous objects: enemy cars and barriers.
    If two lanes are already blocked, a new enemy/barrier must not appear
    in the third free lane. This keeps at least one safe path for the player.
    """
    lanes = set()

    for enemy in enemies:
        if enemy is ignore_sprite:
            continue
        if enemy.rect.bottom > -180 and enemy.rect.top < WINDOW_HEIGHT:
            lanes.add(sprite_lane_index(enemy))

    if obstacles is not None:
        for obs in obstacles:
            if obs is ignore_sprite:
                continue
            if getattr(obs, "kind", None) != "barrier":
                continue
            if obs.rect.bottom > -180 and obs.rect.top < WINDOW_HEIGHT:
                lanes.add(sprite_lane_index(obs))

    return lanes


def is_enemy_position_safe(new_rect, enemies, ignore_enemy=None, min_gap=170):
    """
    Checks that a new enemy car does not appear on top of another enemy car.
    It blocks spawn if:
    1) rectangles touch each other;
    2) cars are in the same lane and too close vertically.
    """
    for enemy in enemies:
        if enemy is ignore_enemy:
            continue

        if new_rect.colliderect(enemy.rect):
            return False

        same_lane = abs(new_rect.centerx - enemy.rect.centerx) < LANE_WIDTH // 2
        too_close = abs(new_rect.centery - enemy.rect.centery) < min_gap

        if same_lane and too_close:
            return False

    return True


# ---------------------------------------------------------------------------
# Main game class
# ---------------------------------------------------------------------------

class RacerGame:
    def __init__(self, screen, settings, username):
        self.screen   = screen
        self.username = username
        diff          = settings.get("difficulty", "medium")
        self.config   = DIFF_CONFIG[diff]

        pygame.display.set_caption("TSIS 03 — Racer")

        self.hud_font  = pygame.font.SysFont("consolas", 19, bold=True)
        self.info_font = pygame.font.SysFont("arial", 16)
        self.big_font  = pygame.font.SysFont("arial", 30, bold=True)
        self.wfont     = pygame.font.SysFont("arial", 15, bold=True)
        self.clock     = pygame.time.Clock()

        self.road_img  = make_road()
        self.coin_base = make_coin()

        self.sound_on = settings.get("sound", False)
        self.sounds   = make_sounds() if self.sound_on else {}

        self.base_speed  = self.config["speed"]
        self.player      = Player(settings.get("car_color", "blue"))

        self.enemies      = pygame.sprite.Group()
        self.coins        = pygame.sprite.Group()
        self.obstacles    = pygame.sprite.Group()
        self.powerups     = pygame.sprite.Group()
        self.road_strips  = pygame.sprite.Group()

        # Stagger enemy start positions so they don't spawn in a pile
        for i in range(self.config["enemies"]):
            e = Enemy(self.base_speed)
            self._place_enemy_safely(e, y_min=-900 - i * 250, y_max=-150 - i * 180)
            self.enemies.add(e)

        self.road_scroll   = 0
        self.coins_collected = 0
        self.powerup_bonus = 0
        self.distance_px   = 0
        self.race_dist_m   = self.config["race_m"]

        self.EV_SPEED    = pygame.USEREVENT + 10
        self.EV_COIN     = pygame.USEREVENT + 11
        self.EV_OBSTACLE = pygame.USEREVENT + 12
        self.EV_POWERUP  = pygame.USEREVENT + 13
        self.EV_STRIP    = pygame.USEREVENT + 14
        pygame.time.set_timer(self.EV_SPEED,    5000)
        pygame.time.set_timer(self.EV_COIN,     self.config["spawn_ms"])
        pygame.time.set_timer(self.EV_OBSTACLE, 2200)
        pygame.time.set_timer(self.EV_POWERUP,  7000)
        pygame.time.set_timer(self.EV_STRIP,    9000)

    def _play(self, name):
        if self.sound_on and name in self.sounds:
            self.sounds[name].play()

    def _all_sprites(self):
        return (list(self.enemies) + list(self.coins) +
                list(self.obstacles) + list(self.powerups))

    def _safe_blocker_lanes(self, ignore_sprite=None):
        """
        Chooses lanes for dangerous objects: enemy cars and barriers.
        If 2 lanes already have dangerous objects, the 3rd lane is blocked for spawn.
        This prevents the game from creating a situation where all lanes are closed.
        """
        occupied = occupied_blocker_lanes(
            self.enemies,
            self.obstacles,
            ignore_sprite=ignore_sprite
        )

        if len(occupied) >= 2:
            return [LANE_CENTERS[i] for i in occupied]

        return LANE_CENTERS[:]

    def _safe_enemy_lanes(self, enemy):
        return self._safe_blocker_lanes(ignore_sprite=enemy)

    def _place_enemy_safely(self, enemy, y_min=-700, y_max=-120):
        """
        Places an enemy car safely:
        1) it cannot overlap another enemy;
        2) it cannot appear too close behind another enemy in the same lane;
        3) it cannot close all 3 lanes at the same time.
        """
        possible_lanes = self._safe_enemy_lanes(enemy)

        for _ in range(60):
            lane = random.choice(possible_lanes)
            y = random.randint(y_min, y_max)

            enemy.rect.centerx = lane
            enemy.rect.y = y

            if is_enemy_position_safe(enemy.rect, self.enemies, ignore_enemy=enemy):
                return

        # Backup: put the car much higher, but still do not use the 3rd free lane
        # when two lanes are already occupied.
        enemy.rect.centerx = random.choice(possible_lanes)
        enemy.rect.y = y_min - 300

    def _effective_speed(self):
        s = self.base_speed
        if self.player.active_powerup == "nitro":
            s = int(s * 1.6)
        elif self.player.slow_frames > 0:
            s = max(2, int(s * 0.55))
        return s

    def _spawn_coin(self):
        if random.random() < 0.25:
            return

        weight = random.choices([1, 2, 3], weights=[60, 30, 10])[0]

        # Coins must not appear in the same lane with a visible/near enemy car
        # or a barrier. This prevents unfair situations where a reward is
        # placed directly on a dangerous lane.
        possible_lanes = [
            lane for lane in LANE_CENTERS
            if is_coin_lane_safe(lane, self.enemies, self.obstacles)
        ]
        random.shuffle(possible_lanes)

        for lane in possible_lanes:
            if is_lane_clear(lane, self._all_sprites(), min_gap=150):
                c = Coin(self.coin_base, self.base_speed + 1, weight, self.wfont)
                c.rect.centerx = lane
                self.coins.add(c)
                return

    def _spawn_obstacle(self):
        if random.random() > self.config["obs_chance"]:
            return

        kind = random.choices(["barrier", "oil", "pothole"], weights=[40, 35, 25])[0]

        # Barrier is dangerous like an enemy car.
        # It must NOT spawn in the 3rd free lane when 2 lanes
        # are already blocked by cars/barriers.
        if kind == "barrier":
            possible_lanes = self._safe_blocker_lanes()
        else:
            possible_lanes = LANE_CENTERS[:]

        random.shuffle(possible_lanes)
        for lane in possible_lanes:
            if is_lane_clear(lane, self._all_sprites()):
                obs = Obstacle(kind, self.base_speed)
                obs.rect.centerx = lane
                self.obstacles.add(obs)
                return

    def _spawn_powerup(self):
        kind = random.choice(["nitro", "shield", "repair"])

        possible_lanes = [
            lane for lane in LANE_CENTERS
            if is_coin_lane_safe(lane, self.enemies, self.obstacles)
        ]
        random.shuffle(possible_lanes)

        for lane in possible_lanes:
            if is_lane_clear(lane, self._all_sprites(), min_gap=150):
                pu = PowerUp(kind, self.base_speed)
                pu.rect.centerx = lane
                self.powerups.add(pu)
                return

    def _spawn_strip(self):
        self.road_strips.add(RoadStrip(random.choice(["nitro", "bump"]), self.base_speed))

    def _increase_difficulty(self):
        self.base_speed += 1
        # Occasionally add an extra enemy, up to a cap
        max_e = self.config["enemies"] + 2
        if len(self.enemies) < max_e and random.random() < 0.4:
            e = Enemy(self.base_speed)
            self._place_enemy_safely(e)
            self.enemies.add(e)

    def _handle_collisions(self):
        # Enemy hit
        hit = pygame.sprite.spritecollideany(self.player, self.enemies)
        if hit:
            if self.player.has_shield:
                self.player.consume_shield()
                self._place_enemy_safely(hit)
            else:
                self._play("crash")
                return "dead"

        # Obstacle hit
        for obs in pygame.sprite.spritecollide(self.player, self.obstacles, False):
            if obs.kind == "barrier":
                if self.player.has_shield:
                    self.player.consume_shield()
                    obs.kill()
                else:
                    self._play("crash")
                    return "dead"
            else:
                # Oil or pothole — slow the player
                self.player.slow_frames = OIL_SLOW_FRAMES
                obs.kill()

        # Power-up collected
        for pu in pygame.sprite.spritecollide(self.player, self.powerups, dokill=True):
            self.player.apply_powerup(pu.kind)
            self.powerup_bonus += 50
            self._play("powerup")

        # Road strip events
        for strip in pygame.sprite.spritecollide(self.player, self.road_strips, False):
            if strip.kind == "nitro" and self.player.active_powerup != "nitro":
                self.player.active_powerup = "nitro"
                self.player.powerup_frames = 2 * FPS
                strip.kill()
            elif strip.kind == "bump":
                self.player.slow_frames = max(self.player.slow_frames, int(1.5 * FPS))
                strip.kill()

        # Coins collected
        for coin in pygame.sprite.spritecollide(self.player, self.coins, dokill=True):
            self.coins_collected += coin.weight
            self._play("coin")

        return "ok"

    @property
    def distance_m(self):
        return self.distance_px // 60

    @property
    def score(self):
        return self.coins_collected * 10 + self.distance_m // 5 + self.powerup_bonus

    def _draw_road(self, scroll_speed):
        self.screen.fill((54, 153, 56))
        self.road_scroll = (self.road_scroll + scroll_speed) % WINDOW_HEIGHT
        self.screen.blit(self.road_img, (ROAD_LEFT, self.road_scroll - WINDOW_HEIGHT))
        self.screen.blit(self.road_img, (ROAD_LEFT, self.road_scroll))

    def _draw_hud(self, scroll_speed):
        # Semi-transparent band at the top for readability
        overlay = pygame.Surface((WINDOW_WIDTH, 108), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 110))
        self.screen.blit(overlay, (0, 0))

        self.screen.blit(self.big_font.render("RACER", True, (245, 245, 245)), (8, 8))

        spd = self.hud_font.render(f"Spd: {scroll_speed}", True, (240, 240, 240))
        self.screen.blit(spd, (8, 48))

        if self.player.has_shield:
            self.screen.blit(self.info_font.render("SHIELD", True, (60, 210, 100)), (8, 76))
        if self.player.slow_frames > 0:
            self.screen.blit(self.info_font.render("SLOW!", True, (255, 170, 40)), (8, 95))

        coins_s = self.hud_font.render(f"Coins: {self.coins_collected}", True, (255, 230, 90))
        self.screen.blit(coins_s, coins_s.get_rect(topright=(WINDOW_WIDTH - 8, 8)))

        score_s = self.hud_font.render(f"Score: {self.score}", True, (210, 240, 255))
        self.screen.blit(score_s, score_s.get_rect(topright=(WINDOW_WIDTH - 8, 34)))

        dist_s = self.info_font.render(
            f"{self.distance_m} / {self.race_dist_m} m", True, (200, 255, 200))
        self.screen.blit(dist_s, dist_s.get_rect(topright=(WINDOW_WIDTH - 8, 60)))

        if self.player.active_powerup == "nitro":
            secs = self.player.powerup_frames // FPS
            ns = self.info_font.render(f"NITRO {secs}s", True, (30, 160, 240))
            self.screen.blit(ns, ns.get_rect(topright=(WINDOW_WIDTH - 8, 82)))

        # Race progress bar at the very bottom
        progress = min(1.0, self.distance_m / self.race_dist_m)
        pygame.draw.rect(self.screen, (40, 40, 40), (ROAD_LEFT, WINDOW_HEIGHT - 6, ROAD_WIDTH, 5))
        pygame.draw.rect(self.screen, (80, 220, 80),
                         (ROAD_LEFT, WINDOW_HEIGHT - 6, int(ROAD_WIDTH * progress), 5))

        ctrl = self.info_font.render("← → move   Esc = quit", True, (200, 200, 200))
        self.screen.blit(ctrl, (8, WINDOW_HEIGHT - 26))

    def run(self):
        result = None
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_LEFT:
                        self.player.move_left()
                    elif event.key == pygame.K_RIGHT:
                        self.player.move_right()
                elif event.type == self.EV_SPEED:
                    self._increase_difficulty()
                elif event.type == self.EV_COIN:
                    self._spawn_coin()
                elif event.type == self.EV_OBSTACLE:
                    self._spawn_obstacle()
                elif event.type == self.EV_POWERUP:
                    self._spawn_powerup()
                elif event.type == self.EV_STRIP:
                    self._spawn_strip()

            scroll_speed = self._effective_speed()
            self.distance_px += scroll_speed
            self.player.tick()

            for e in self.enemies:
                e.update(self.base_speed)
                if e.rect.top > WINDOW_HEIGHT:
                    self._place_enemy_safely(e)
            for c in list(self.coins):
                c.update(self.base_speed + 1)
            for obs in list(self.obstacles):
                obs.update(self.base_speed)
            for pu in list(self.powerups):
                pu.update(self.base_speed)
            for rs in list(self.road_strips):
                rs.update(self.base_speed)

            if self._handle_collisions() == "dead":
                result = {"score": self.score, "distance": self.distance_m,
                          "coins": self.coins_collected, "won": False}
                running = False

            if self.distance_m >= self.race_dist_m:
                result = {"score": self.score + 500, "distance": self.distance_m,
                          "coins": self.coins_collected, "won": True}
                running = False

            # Draw
            self._draw_road(scroll_speed)
            for rs in self.road_strips:
                self.screen.blit(rs.image, rs.rect)
            for obs in self.obstacles:
                self.screen.blit(obs.image, obs.rect)
            for pu in self.powerups:
                self.screen.blit(pu.image, pu.rect)
            for e in self.enemies:
                self.screen.blit(e.image, e.rect)
            for c in self.coins:
                self.screen.blit(c.image, c.rect)
                c.draw_label(self.screen)
            self.screen.blit(self.player.image, self.player.rect)
            self._draw_hud(scroll_speed)

            pygame.display.flip()
            self.clock.tick(FPS)

        # Cancel all custom timers to avoid leaking into menu screens
        for ev_id in (self.EV_SPEED, self.EV_COIN, self.EV_OBSTACLE,
                      self.EV_POWERUP, self.EV_STRIP):
            pygame.time.set_timer(ev_id, 0)

        if result is None:
            result = {"score": self.score, "distance": self.distance_m,
                      "coins": self.coins_collected, "won": False}
        return result