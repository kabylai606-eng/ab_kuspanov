import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import pygame
from persistence import load_settings, save_settings, add_score
from ui import show_main_menu, show_name_entry, show_settings, show_leaderboard, show_game_over
from racer import RacerGame


def main():
    pygame.init()
    screen = pygame.display.set_mode((420, 700))
    pygame.display.set_caption("TSIS 03 — Racer")

    settings = load_settings()
    username = ""
    state    = "menu"

    while state != "quit":
        if state == "menu":
            state = show_main_menu(screen)

        elif state == "play":
            # Ask for a name before every new game run
            name = show_name_entry(screen, default=username)
            if name is None:
                state = "menu"
            else:
                username = name
                state = "game"

        elif state == "game":
            game   = RacerGame(screen, settings, username)
            result = game.run()
            add_score(username, result["score"], result["distance"], result["coins"])
            after = show_game_over(screen, result)
            if after == "retry":
                state = "game"
            elif after == "menu":
                state = "menu"
            else:
                state = "quit"

        elif state == "leaderboard":
            state = show_leaderboard(screen)

        elif state == "settings":
            new_s = show_settings(screen, settings)
            if new_s is not None:
                settings = new_s
                save_settings(settings)
            state = "menu"

    pygame.quit()


if __name__ == "__main__":
    main()