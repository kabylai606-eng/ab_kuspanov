import pygame
from persistence import load_leaderboard

BG       = (18, 20, 32)
BTN      = (50, 75, 130)
BTN_HOV  = (75, 115, 185)
BORDER   = (90, 130, 200)
WHITE    = (225, 228, 235)
GOLD     = (255, 200, 40)
DIM      = (150, 155, 165)
GREEN    = (80, 210, 100)
RED      = (255, 80, 80)


def make_fonts():
    return {
        "title": pygame.font.SysFont("arial", 44, bold=True),
        "big":   pygame.font.SysFont("arial", 28, bold=True),
        "mid":   pygame.font.SysFont("arial", 22),
        "small": pygame.font.SysFont("arial", 17),
        "tiny":  pygame.font.SysFont("arial", 14),
    }


def draw_button(screen, rect, text, font, hovered=False):
    pygame.draw.rect(screen, BTN_HOV if hovered else BTN, rect, border_radius=9)
    pygame.draw.rect(screen, BORDER, rect, width=2, border_radius=9)
    lbl = font.render(text, True, WHITE)
    screen.blit(lbl, lbl.get_rect(center=rect.center))


def show_main_menu(screen):
    fonts = make_fonts()
    W, H = screen.get_size()
    cx = W // 2
    bw, bh = 220, 50

    buttons = {
        "play":        pygame.Rect(cx - bw // 2, 260, bw, bh),
        "leaderboard": pygame.Rect(cx - bw // 2, 325, bw, bh),
        "settings":    pygame.Rect(cx - bw // 2, 390, bw, bh),
        "quit":        pygame.Rect(cx - bw // 2, 455, bw, bh),
    }
    labels = {"play": "PLAY", "leaderboard": "LEADERBOARD",
              "settings": "SETTINGS", "quit": "QUIT"}

    clock = pygame.time.Clock()
    while True:
        mx, my = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return "quit"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for name, rect in buttons.items():
                    if rect.collidepoint(mx, my):
                        return name

        screen.fill(BG)
        t = fonts["title"].render("RACER", True, GOLD)
        screen.blit(t, t.get_rect(center=(cx, 160)))
        sub = fonts["small"].render("Advanced Edition — TSIS 03", True, DIM)
        screen.blit(sub, sub.get_rect(center=(cx, 212)))

        for name, rect in buttons.items():
            draw_button(screen, rect, labels[name], fonts["mid"], rect.collidepoint(mx, my))

        pygame.display.flip()
        clock.tick(60)


def show_name_entry(screen, default=""):
    fonts = make_fonts()
    W, H = screen.get_size()
    cx = W // 2
    buf = default
    input_rect = pygame.Rect(cx - 140, 340, 280, 50)
    ok_btn     = pygame.Rect(cx - 100, 420, 200, 48)

    clock = pygame.time.Clock()
    while True:
        mx, my = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None
                elif event.key == pygame.K_RETURN and buf.strip():
                    return buf.strip()
                elif event.key == pygame.K_BACKSPACE:
                    buf = buf[:-1]
                elif event.unicode.isprintable() and len(buf) < 18:
                    buf += event.unicode
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if ok_btn.collidepoint(mx, my) and buf.strip():
                    return buf.strip()

        screen.fill(BG)
        prompt = fonts["big"].render("Enter your name", True, GOLD)
        screen.blit(prompt, prompt.get_rect(center=(cx, 270)))

        pygame.draw.rect(screen, (28, 32, 50), input_rect, border_radius=8)
        pygame.draw.rect(screen, BORDER, input_rect, width=2, border_radius=8)
        name_surf = fonts["mid"].render(buf + "|", True, WHITE)
        screen.blit(name_surf, name_surf.get_rect(midleft=(input_rect.x + 12, input_rect.centery)))

        draw_button(screen, ok_btn, "START", fonts["mid"], ok_btn.collidepoint(mx, my))
        pygame.display.flip()
        clock.tick(60)


def show_settings(screen, settings):
    fonts = make_fonts()
    W, H = screen.get_size()
    cx = W // 2

    s = dict(settings)
    CAR_COLORS   = ["blue", "red", "green", "yellow"]
    DIFFICULTIES = ["easy", "medium", "hard"]

    save_btn = pygame.Rect(65,  560, 135, 42)
    back_btn = pygame.Rect(220, 560, 135, 42)

    clock = pygame.time.Clock()
    while True:
        mx, my = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return None
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                sound_box = pygame.Rect(cx + 20, 232, 26, 26)
                color_box  = pygame.Rect(cx + 20, 302, 130, 30)
                diff_box   = pygame.Rect(cx + 20, 372, 130, 30)

                if sound_box.collidepoint(mx, my):
                    s["sound"] = not s["sound"]

                if color_box.collidepoint(mx, my):
                    try:
                        i = CAR_COLORS.index(s["car_color"])
                    except ValueError:
                        i = 0
                    s["car_color"] = CAR_COLORS[(i + 1) % len(CAR_COLORS)]

                if diff_box.collidepoint(mx, my):
                    try:
                        i = DIFFICULTIES.index(s["difficulty"])
                    except ValueError:
                        i = 1
                    s["difficulty"] = DIFFICULTIES[(i + 1) % len(DIFFICULTIES)]

                if save_btn.collidepoint(mx, my):
                    return s
                if back_btn.collidepoint(mx, my):
                    return None

        screen.fill(BG)
        title = fonts["big"].render("SETTINGS", True, GOLD)
        screen.blit(title, title.get_rect(center=(cx, 150)))

        # Sound toggle
        screen.blit(fonts["mid"].render("Sound:", True, WHITE), (50, 236))
        sb = pygame.Rect(cx + 20, 232, 26, 26)
        pygame.draw.rect(screen, (28, 32, 50), sb, border_radius=5)
        pygame.draw.rect(screen, BORDER, sb, width=2, border_radius=5)
        if s["sound"]:
            pygame.draw.rect(screen, GREEN, sb.inflate(-8, -8), border_radius=3)

        # Car color cycle button
        screen.blit(fonts["mid"].render("Car color:", True, WHITE), (50, 306))
        cb = pygame.Rect(cx + 20, 302, 130, 30)
        draw_button(screen, cb, s["car_color"].upper(), fonts["small"], cb.collidepoint(mx, my))

        # Difficulty cycle button
        screen.blit(fonts["mid"].render("Difficulty:", True, WHITE), (50, 376))
        db = pygame.Rect(cx + 20, 372, 130, 30)
        draw_button(screen, db, s["difficulty"].upper(), fonts["small"], db.collidepoint(mx, my))

        hint = fonts["tiny"].render("Click buttons to cycle options", True, DIM)
        screen.blit(hint, hint.get_rect(center=(cx, 430)))

        draw_button(screen, save_btn, "SAVE", fonts["small"], save_btn.collidepoint(mx, my))
        draw_button(screen, back_btn, "BACK", fonts["small"], back_btn.collidepoint(mx, my))
        pygame.display.flip()
        clock.tick(60)


def show_leaderboard(screen):
    fonts = make_fonts()
    W, H = screen.get_size()
    cx = W // 2
    back_btn = pygame.Rect(cx - 100, 640, 200, 46)
    entries = load_leaderboard()

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
        title = fonts["big"].render("TOP 10  LEADERBOARD", True, GOLD)
        screen.blit(title, title.get_rect(center=(cx, 80)))

        col_x = [20, 55, 185, 270, 355]
        headers = ["#", "Name", "Score", "Dist m", "Coins"]
        for x, h in zip(col_x, headers):
            screen.blit(fonts["small"].render(h, True, DIM), (x, 130))
        pygame.draw.line(screen, DIM, (15, 154), (W - 15, 154), 1)

        for rank, e in enumerate(entries[:10], 1):
            y = 164 + (rank - 1) * 43
            color = GOLD if rank == 1 else WHITE
            row = [str(rank), e["name"][:13], str(e["score"]),
                   str(e["distance"]), str(e["coins"])]
            for x, val in zip(col_x, row):
                screen.blit(fonts["small"].render(val, True, color), (x, y))

        if not entries:
            msg = fonts["mid"].render("No scores yet — play first!", True, DIM)
            screen.blit(msg, msg.get_rect(center=(cx, 380)))

        draw_button(screen, back_btn, "BACK", fonts["mid"], back_btn.collidepoint(mx, my))
        pygame.display.flip()
        clock.tick(60)


def show_game_over(screen, result):
    fonts = make_fonts()
    W, H = screen.get_size()
    cx = W // 2
    retry_btn = pygame.Rect(12,  540, 185, 48)
    menu_btn  = pygame.Rect(223, 540, 185, 48)

    won = result.get("won", False)
    headline       = "YOU WIN!" if won else "GAME OVER"
    headline_color = GREEN if won else RED

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
        hl = fonts["title"].render(headline, True, headline_color)
        screen.blit(hl, hl.get_rect(center=(cx, 200)))

        lines = [
            f"Score:    {result['score']}",
            f"Distance: {result['distance']} m",
            f"Coins:    {result['coins']}",
        ]
        for i, line in enumerate(lines):
            s = fonts["mid"].render(line, True, WHITE)
            screen.blit(s, s.get_rect(center=(cx, 300 + i * 50)))

        draw_button(screen, retry_btn, "RETRY  (R)", fonts["mid"], retry_btn.collidepoint(mx, my))
        draw_button(screen, menu_btn,  "MAIN MENU",  fonts["mid"], menu_btn.collidepoint(mx, my))

        hint = fonts["tiny"].render("R = retry   Esc = main menu", True, DIM)
        screen.blit(hint, hint.get_rect(center=(cx, 608)))
        pygame.display.flip()
        clock.tick(60)