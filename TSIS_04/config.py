import json
from pathlib import Path

CELL_SIZE  = 25
GRID_COLS  = 24
GRID_ROWS  = 24
HUD_HEIGHT = 70

WINDOW_WIDTH  = GRID_COLS * CELL_SIZE        # 600
WINDOW_HEIGHT = HUD_HEIGHT + GRID_ROWS * CELL_SIZE  # 670

BASE_SPEED           = 7
FOODS_PER_LEVEL      = 4
FOOD_LIFETIME_MS     = 5000
POWERUP_LIFETIME_MS  = 8000   # field lifetime before disappearing
POWERUP_EFFECT_MS    = 5000   # duration of speed boost / slow motion
OBSTACLE_COUNT       = 3      # blocks added per level from level 3

SETTINGS_FILE = Path(__file__).parent / "settings.json"

DEFAULT_SETTINGS = {
    "snake_color": [45, 185, 70],
    "grid_overlay": True,
    "sound": False,
}


def load_settings():
    if SETTINGS_FILE.exists():
        with open(SETTINGS_FILE) as f:
            data = json.load(f)
        return {**DEFAULT_SETTINGS, **data}
    return dict(DEFAULT_SETTINGS)


def save_settings(settings):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=2)