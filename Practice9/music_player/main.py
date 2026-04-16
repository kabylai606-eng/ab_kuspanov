import sys
from pathlib import Path

import pygame

CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from player import MusicPlayer


def run_music_player():
    pygame.init()
    pygame.display.set_caption("Practice 09 - Music Player")

    screen = pygame.display.set_mode((900, 500))
    clock = pygame.time.Clock()
    title_font = pygame.font.SysFont("arial", 40, bold=True)
    text_font = pygame.font.SysFont("arial", 28)

    try:
        player = MusicPlayer()
    except RuntimeError as error:
        print(error)
        pygame.quit()
        return

    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                action = player.handle_event(event)
                if action == "quit":
                    running = False

        player.update()
        player.draw_ui(screen, title_font, text_font)
        pygame.display.flip()
        clock.tick(30)

    player.close()
    pygame.quit()


if __name__ == "__main__":
    run_music_player()