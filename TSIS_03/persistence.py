import json
from pathlib import Path

SETTINGS_FILE = Path(__file__).parent / "settings.json"
LEADERBOARD_FILE = Path(__file__).parent / "leaderboard.json"

DEFAULT_SETTINGS = {
    "sound": False,
    "car_color": "blue",
    "difficulty": "medium",
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


def load_leaderboard():
    if LEADERBOARD_FILE.exists():
        with open(LEADERBOARD_FILE) as f:
            return json.load(f)
    return []


def save_leaderboard(entries):
    with open(LEADERBOARD_FILE, "w") as f:
        json.dump(entries, f, indent=2)


def add_score(name, score, distance, coins):
    entries = load_leaderboard()

    # Deduplicate existing entries — one record per player, keep their best
    best_by_name = {}
    for e in entries:
        n = e["name"]
        if n not in best_by_name or e["score"] > best_by_name[n]["score"]:
            best_by_name[n] = e

    # Add or update this player's record only when they beat their own best
    if name not in best_by_name or score > best_by_name[name]["score"]:
        best_by_name[name] = {"name": name, "score": score,
                               "distance": distance, "coins": coins}

    entries = sorted(best_by_name.values(), key=lambda e: e["score"], reverse=True)[:10]
    save_leaderboard(entries)