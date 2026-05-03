import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import pygame
import db
from config import load_settings, save_settings, WINDOW_WIDTH, WINDOW_HEIGHT
from game import SnakeGame

BG     = (18, 20, 32)
BTN    = (50, 75, 130)
HOVER  = (75, 115, 185)
BORDER = (90, 130, 200)
WHITE  = (225, 228, 235)
GOLD   = (255, 200, 40)
DIM    = (150, 155, 165)
GREEN  = (80, 210, 100)
RED    = (255, 80, 80)


def make_fonts():
    return {
        "title": pygame.font.SysFont("arial", 42, bold=True),
        "big":   pygame.font.SysFont("arial", 28, bold=True),
        "mid":   pygame.font.SysFont("arial", 22),
        "small": pygame.font.SysFont("arial", 17),
        "tiny":  pygame.font.SysFont("arial", 14),
    }


def draw_button(screen, rect, text, font, hovered=False):
    pygame.draw.rect(screen, HOVER if hovered else BTN, rect, border_radius=9)
    pygame.draw.rect(screen, BORDER, rect, width=2, border_radius=9)
    lbl = font.render(text, True, WHITE)
    screen.blit(lbl, lbl.get_rect(center=rect.center))


def show_main_menu(screen, db_ok):
    fonts = make_fonts()
    W, H  = screen.get_size()
    cx    = W // 2
    bw, bh = 230, 50

    buttons = {
        "play":        pygame.Rect(cx - bw // 2, 260, bw, bh),
        "leaderboard": pygame.Rect(cx - bw // 2, 325, bw, bh),
        "settings":    pygame.Rect(cx - bw // 2, 390, bw, bh),
        "quit":        pygame.Rect(cx - bw // 2, 455, bw, bh),
    }

    # Username input (shown below the title)
    username_buf  = ""
    input_rect    = pygame.Rect(cx - 140, 160, 280, 44)
    db_label      = "DB: connected" if db_ok else "DB: offline (scores not saved)"
    db_color      = (60, 210, 100) if db_ok else (220, 100, 50)

    clock = pygame.time.Clock()
    while True:
        mx, my = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit", ""
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "quit", ""
                elif event.key == pygame.K_RETURN and username_buf.strip():
                    return "play", username_buf.strip()
                elif event.key == pygame.K_BACKSPACE:
                    username_buf = username_buf[:-1]
                elif event.unicode.isprintable() and len(username_buf) < 18:
                    username_buf += event.unicode
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for name, rect in buttons.items():
                    if rect.collidepoint(mx, my):
                        if name == "play" and not username_buf.strip():
                            pass  # don't start without a name
                        else:
                            return name, username_buf.strip()

        screen.fill(BG)

        title = fonts["title"].render("SNAKE", True, GOLD)
        screen.blit(title, title.get_rect(center=(cx, 90)))

        # Username label + input box
        screen.blit(fonts["small"].render("Username:", True, DIM), (cx - 140, 140))
        pygame.draw.rect(screen, (28, 32, 50), input_rect, border_radius=8)
        pygame.draw.rect(screen, BORDER, input_rect, width=2, border_radius=8)
        name_surf = fonts["mid"].render(username_buf + "|", True, WHITE)
        screen.blit(name_surf, name_surf.get_rect(midleft=(input_rect.x + 10, input_rect.centery)))

        screen.blit(fonts["tiny"].render(db_label, True, db_color),
                    (cx - 140, input_rect.bottom + 6))

        labels = {"play": "PLAY", "leaderboard": "LEADERBOARD",
                  "settings": "SETTINGS", "quit": "QUIT"}
        for name, rect in buttons.items():
            draw_button(screen, rect, labels[name], fonts["mid"], rect.collidepoint(mx, my))

        hint = fonts["tiny"].render("Enter a name then press PLAY or Enter", True, DIM)
        screen.blit(hint, hint.get_rect(center=(cx, 220)))

        pygame.display.flip()
        clock.tick(60)


def show_settings(screen, settings):
    fonts = make_fonts()
    W, H  = screen.get_size()
    cx    = W // 2
    s     = dict(settings)

    # Preset snake colors to cycle through
    SNAKE_COLORS = [
        [45, 185, 70], [40, 120, 255], [225, 64, 64],
        [255, 200, 40], [180, 80, 255],
    ]
    COLOR_NAMES = ["Green", "Blue", "Red", "Yellow", "Purple"]

    save_btn = pygame.Rect(cx - 110, 500, 200, 46)
    back_btn = pygame.Rect(cx - 110, 556, 200, 46)

    clock = pygame.time.Clock()
    while True:
        mx, my = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return None
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                grid_box  = pygame.Rect(cx + 30, 252, 26, 26)
                sound_box = pygame.Rect(cx + 30, 312, 26, 26)
                color_btn = pygame.Rect(cx + 30, 370, 130, 30)

                if grid_box.collidepoint(mx, my):
                    s["grid_overlay"] = not s["grid_overlay"]
                if sound_box.collidepoint(mx, my):
                    s["sound"] = not s["sound"]
                if color_btn.collidepoint(mx, my):
                    cur = s["snake_color"]
                    try:
                        i = SNAKE_COLORS.index(cur)
                    except ValueError:
                        i = 0
                    s["snake_color"] = SNAKE_COLORS[(i + 1) % len(SNAKE_COLORS)]
                if save_btn.collidepoint(mx, my):
                    return s
                if back_btn.collidepoint(mx, my):
                    return None

        screen.fill(BG)
        screen.blit(fonts["big"].render("SETTINGS", True, GOLD),
                    fonts["big"].render("SETTINGS", True, GOLD).get_rect(center=(cx, 160)))

        def checkbox(label, rect, checked, y):
            screen.blit(fonts["mid"].render(label, True, WHITE), (cx - 160, y + 3))
            pygame.draw.rect(screen, (28, 32, 50), rect, border_radius=5)
            pygame.draw.rect(screen, BORDER, rect, width=2, border_radius=5)
            if checked:
                pygame.draw.rect(screen, GREEN, rect.inflate(-8, -8), border_radius=3)

        checkbox("Grid overlay:", pygame.Rect(cx + 30, 252, 26, 26), s["grid_overlay"], 252)
        checkbox("Sound:",        pygame.Rect(cx + 30, 312, 26, 26), s["sound"],        312)

        screen.blit(fonts["mid"].render("Snake color:", True, WHITE), (cx - 160, 374))
        # Color preview square
        pygame.draw.rect(screen, tuple(s["snake_color"]),
                         pygame.Rect(cx + 30, 370, 30, 30), border_radius=4)
        # Cycle button
        try:
            color_name = COLOR_NAMES[SNAKE_COLORS.index(s["snake_color"])]
        except ValueError:
            color_name = "Custom"
        cb = pygame.Rect(cx + 68, 370, 92, 30)
        draw_button(screen, cb, color_name, fonts["tiny"], cb.collidepoint(mx, my))

        draw_button(screen, save_btn, "SAVE & BACK", fonts["mid"], save_btn.collidepoint(mx, my))
        draw_button(screen, back_btn, "BACK",        fonts["mid"], back_btn.collidepoint(mx, my))

        pygame.display.flip()
        clock.tick(60)


def show_leaderboard(screen, db_ok):
    fonts    = make_fonts()
    W, H     = screen.get_size()
    cx       = W // 2
    back_btn = pygame.Rect(cx - 100, H - 60, 200, 46)

    entries = []
    if db_ok:
        try:
            entries = db.get_leaderboard()
        except Exception:
            db_ok = False

    clock = pygame.time.Clock()
    while True:
        mx, my = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return "menu"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if back_btn.collidepoint(mx, my):
                    return "menu"

        screen.fill(BG)
        screen.blit(fonts["big"].render("TOP 10  LEADERBOARD", True, GOLD),
                    fonts["big"].render("TOP 10  LEADERBOARD", True, GOLD).get_rect(center=(cx, 65)))

        col_x   = [20, 55, 190, 295, 400, 500]
        headers = ["#", "Name", "Score", "Level", "Date"]
        for x, h in zip(col_x, headers):
            screen.blit(fonts["small"].render(h, True, DIM), (x, 110))
        pygame.draw.line(screen, DIM, (15, 133), (W - 15, 133), 1)

        if not db_ok or not entries:
            msg = "DB offline — no scores available" if not db_ok else "No scores yet"
            screen.blit(fonts["mid"].render(msg, True, DIM),
                        fonts["mid"].render(msg, True, DIM).get_rect(center=(cx, 350)))
        else:
            for rank, row in enumerate(entries[:10], 1):
                y     = 143 + (rank - 1) * 42
                color = GOLD if rank == 1 else WHITE
                vals  = [str(rank), str(row[0])[:13], str(row[1]), str(row[2]), str(row[3])]
                for x, v in zip(col_x, vals):
                    screen.blit(fonts["small"].render(v, True, color), (x, y))

        draw_button(screen, back_btn, "BACK", fonts["mid"], back_btn.collidepoint(mx, my))
        pygame.display.flip()
        clock.tick(60)


def show_game_over(screen, result, personal_best):
    fonts    = make_fonts()
    W, H     = screen.get_size()
    cx       = W // 2
    retry_btn = pygame.Rect(cx - 220, 500, 190, 48)
    menu_btn  = pygame.Rect(cx + 30,  500, 190, 48)

    clock = pygame.time.Clock()
    while True:
        mx, my = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return "retry"
                if event.key == pygame.K_ESCAPE:
                    return "menu"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if retry_btn.collidepoint(mx, my):
                    return "retry"
                if menu_btn.collidepoint(mx, my):
                    return "menu"

        screen.fill(BG)
        screen.blit(fonts["title"].render("GAME OVER", True, RED),
                    fonts["title"].render("GAME OVER", True, RED).get_rect(center=(cx, 190)))

        lines = [
            f"Score:        {result['score']}",
            f"Level reached: {result['level']}",
            f"Personal best: {personal_best}",
        ]
        for i, line in enumerate(lines):
            s = fonts["mid"].render(line, True, WHITE)
            screen.blit(s, s.get_rect(center=(cx, 295 + i * 52)))

        draw_button(screen, retry_btn, "RETRY  (R)",  fonts["mid"], retry_btn.collidepoint(mx, my))
        draw_button(screen, menu_btn,  "MAIN MENU",   fonts["mid"], menu_btn.collidepoint(mx, my))

        hint = fonts["tiny"].render("R = retry   Esc = main menu", True, DIM)
        screen.blit(hint, hint.get_rect(center=(cx, 565)))
        pygame.display.flip()
        clock.tick(60)


def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("TSIS 04 — Snake")

    settings = load_settings()

    # Try to connect to DB; game still works without it
    db_ok = False
    try:
        db.ensure_tables()
        db_ok = True
    except Exception as e:
        print(f"[DB] Not available: {e}")

    username = ""
    state    = "menu"

    while state != "quit":
        if state == "menu":
            state, username = show_main_menu(screen, db_ok)

        elif state == "play":
            personal_best = 0
            if db_ok and username:
                try:
                    personal_best = db.get_personal_best(username)
                except Exception:
                    pass

            game   = SnakeGame(screen, settings, username, personal_best, db_ok)
            result = game.run()

            if db_ok and username:
                try:
                    db.save_result(username, result["score"], result["level"])
                    personal_best = db.get_personal_best(username)
                except Exception:
                    pass

            after = show_game_over(screen, result, personal_best)
            if after == "retry":
                state = "play"
            elif after == "menu":
                state = "menu"
            else:
                state = "quit"

        elif state == "leaderboard":
            state = show_leaderboard(screen, db_ok)

        elif state == "settings":
            new_s = show_settings(screen, settings)
            if new_s is not None:
                settings = new_s
                save_settings(settings)
            state = "menu"

    pygame.quit()


if __name__ == "__main__":
    main()