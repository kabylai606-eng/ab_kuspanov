import pygame
import sys
from pygame.locals import *

pygame.init()  # запуск pygame

# размеры окна
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 650
TOOLBAR_HEIGHT = 90

# область для рисования без toolbar
CANVAS_RECT = pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT - TOOLBAR_HEIGHT)

# основные цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)
TOOLBAR_BG = (40, 40, 40)
HIGHLIGHT = (180, 180, 255)

# палитра цветов
PALETTE = [
    (0, 0, 0),
    (255, 255, 255),
    (220, 50, 50),
    (50, 200, 50),
    (50, 50, 220),
    (255, 165, 0),
    (255, 255, 0),
    (160, 32, 240),
    (0, 220, 220),
    (255, 20, 147),
    (139, 69, 19),
    (128, 128, 128),
]

# инструменты
TOOL_PENCIL = "pencil"
TOOL_RECTANGLE = "rectangle"
TOOL_SQUARE = "square"
TOOL_CIRCLE = "circle"
TOOL_RIGHT_TRI = "right_tri"
TOOL_EQUIL_TRI = "equil_tri"
TOOL_RHOMBUS = "rhombus"
TOOL_ERASER = "eraser"

# создание окна
DISPLAYSURF = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Paint – Practice 11")

# поверхность для рисования
canvas = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT - TOOLBAR_HEIGHT))
canvas.fill(WHITE)

# шрифт интерфейса
font_ui = pygame.font.SysFont("Verdana", 13)

# состояние программы
current_tool = TOOL_PENCIL
current_color = BLACK
brush_size = 5
eraser_size = 20
drawing = False
start_pos = None
last_pos = None


# ограничивает точку внутри canvas
def clamp_to_canvas(pos):
    x = max(0, min(pos[0], SCREEN_WIDTH - 1))
    y = max(0, min(pos[1], SCREEN_HEIGHT - TOOLBAR_HEIGHT - 1))
    return x, y


# создает прямоугольник по двум точкам
def rect_from_drag(start, end):
    x = min(start[0], end[0])
    y = min(start[1], end[1])
    w = abs(end[0] - start[0])
    h = abs(end[1] - start[1])
    return x, y, w, h


# создает квадрат по движению мыши
def square_from_drag(start, end):
    x, y, w, h = rect_from_drag(start, end)
    side = min(w, h)
    return x, y, side


# точки прямоугольного треугольника
def right_triangle_points(start, end):
    x, y, w, h = rect_from_drag(start, end)

    return [
        (x, y + h),
        (x, y),
        (x + w, y + h),
    ]


# точки равностороннего треугольника
def equilateral_triangle_points(start, end):
    x, y, w, h = rect_from_drag(start, end)

    apex = (x + w // 2, y)
    bottom_left = (x, y + h)
    bottom_right = (x + w, y + h)

    return [apex, bottom_left, bottom_right]


# точки ромба
def rhombus_points(start, end):
    x, y, w, h = rect_from_drag(start, end)

    return [
        (x + w // 2, y),
        (x + w, y + h // 2),
        (x + w // 2, y + h),
        (x, y + h // 2),
    ]


# показывает временный preview фигуры
def draw_shape_preview(surface, tool, start, end, color):
    if tool == TOOL_RECTANGLE:
        x, y, w, h = rect_from_drag(start, end)
        if w > 0 and h > 0:
            pygame.draw.rect(surface, color, (x, y, w, h), 2)

    elif tool == TOOL_SQUARE:
        x, y, side = square_from_drag(start, end)
        if side > 0:
            pygame.draw.rect(surface, color, (x, y, side, side), 2)

    elif tool == TOOL_CIRCLE:
        x, y, w, h = rect_from_drag(start, end)
        radius = min(w, h) // 2
        center = (x + w // 2, y + h // 2)
        if radius > 0:
            pygame.draw.circle(surface, color, center, radius, 2)

    elif tool == TOOL_RIGHT_TRI:
        pygame.draw.polygon(surface, color, right_triangle_points(start, end), 2)

    elif tool == TOOL_EQUIL_TRI:
        pygame.draw.polygon(surface, color, equilateral_triangle_points(start, end), 2)

    elif tool == TOOL_RHOMBUS:
        pygame.draw.polygon(surface, color, rhombus_points(start, end), 2)


# сохраняет фигуру на canvas
def commit_shape(tool, start, end, color):
    if tool == TOOL_RECTANGLE:
        x, y, w, h = rect_from_drag(start, end)
        if w > 0 and h > 0:
            pygame.draw.rect(canvas, color, (x, y, w, h))

    elif tool == TOOL_SQUARE:
        x, y, side = square_from_drag(start, end)
        if side > 0:
            pygame.draw.rect(canvas, color, (x, y, side, side))

    elif tool == TOOL_CIRCLE:
        x, y, w, h = rect_from_drag(start, end)
        radius = min(w, h) // 2
        center = (x + w // 2, y + h // 2)
        if radius > 0:
            pygame.draw.circle(canvas, color, center, radius)

    elif tool == TOOL_RIGHT_TRI:
        pygame.draw.polygon(canvas, color, right_triangle_points(start, end))

    elif tool == TOOL_EQUIL_TRI:
        pygame.draw.polygon(canvas, color, equilateral_triangle_points(start, end))

    elif tool == TOOL_RHOMBUS:
        pygame.draw.polygon(canvas, color, rhombus_points(start, end))


# первая строка кнопок
TOOLS_ROW1 = [
    (TOOL_PENCIL, "Pencil"),
    (TOOL_RECTANGLE, "Rect"),
    (TOOL_SQUARE, "Square"),
    (TOOL_CIRCLE, "Circle"),
]

# вторая строка кнопок
TOOLS_ROW2 = [
    (TOOL_RIGHT_TRI, "R.Tri"),
    (TOOL_EQUIL_TRI, "Eq.Tri"),
    (TOOL_RHOMBUS, "Rhombus"),
    (TOOL_ERASER, "Eraser"),
]

# размеры кнопок
BTN_W = 80
BTN_H = 26


# y-координата toolbar
def tb_y():
    return SCREEN_HEIGHT - TOOLBAR_HEIGHT


# прямоугольник кнопки инструмента
def tool_btn_rect(row, col):
    return pygame.Rect(
        10 + col * (BTN_W + 5),
        tb_y() + 8 + row * (BTN_H + 6),
        BTN_W,
        BTN_H
    )


# прямоугольник цвета в палитре
def swatch_rect(index):
    start_x = 10 + 4 * (BTN_W + 5) + 10

    return pygame.Rect(
        start_x + index * 34,
        tb_y() + 8,
        30,
        30
    )


# рисует toolbar
def draw_toolbar():
    pygame.draw.rect(
        DISPLAYSURF,
        TOOLBAR_BG,
        (0, tb_y(), SCREEN_WIDTH, TOOLBAR_HEIGHT)
    )

    # рисует кнопки инструментов
    for row_idx, row in enumerate([TOOLS_ROW1, TOOLS_ROW2]):
        for col_idx, (tool_id, label) in enumerate(row):
            rect = tool_btn_rect(row_idx, col_idx)

            if tool_id == current_tool:
                color = HIGHLIGHT
            else:
                color = GRAY

            pygame.draw.rect(DISPLAYSURF, color, rect, border_radius=4)
            pygame.draw.rect(DISPLAYSURF, DARK_GRAY, rect, 1, border_radius=4)

            text = font_ui.render(label, True, BLACK)
            DISPLAYSURF.blit(text, text.get_rect(center=rect.center))

    # рисует палитру цветов
    for i, color in enumerate(PALETTE):
        swatch = swatch_rect(i)

        pygame.draw.rect(DISPLAYSURF, color, swatch)

        if color == current_color:
            border = (255, 255, 0)
        else:
            border = DARK_GRAY

        pygame.draw.rect(DISPLAYSURF, border, swatch, 2)

    # показывает активный цвет
    start_x = 10 + 4 * (BTN_W + 5) + 10
    preview_rect = pygame.Rect(
        start_x,
        tb_y() + 44,
        30 + (len(PALETTE) - 1) * 34,
        20
    )

    pygame.draw.rect(DISPLAYSURF, current_color, preview_rect)

    text_color = WHITE if sum(current_color) < 380 else BLACK
    label = font_ui.render("Active color", True, text_color)
    DISPLAYSURF.blit(label, label.get_rect(center=preview_rect.center))


# обрабатывает клик по toolbar
def handle_toolbar_click(pos):
    global current_tool, current_color

    # выбор инструмента
    for row_idx, row in enumerate([TOOLS_ROW1, TOOLS_ROW2]):
        for col_idx, (tool_id, _) in enumerate(row):
            if tool_btn_rect(row_idx, col_idx).collidepoint(pos):
                current_tool = tool_id
                return

    # выбор цвета
    for i, color in enumerate(PALETTE):
        if swatch_rect(i).collidepoint(pos):
            current_color = color
            return


# часы для FPS
clock = pygame.time.Clock()


# главный цикл программы
while True:
    clock.tick(60)

    mouse_pos = pygame.mouse.get_pos()
    in_canvas = CANVAS_RECT.collidepoint(mouse_pos)

    # обработка событий
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

        # нажатие левой кнопки мыши
        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            if in_canvas:
                drawing = True
                start_pos = clamp_to_canvas(mouse_pos)
                last_pos = clamp_to_canvas(mouse_pos)
            else:
                handle_toolbar_click(mouse_pos)

        # отпускание левой кнопки мыши
        if event.type == MOUSEBUTTONUP and event.button == 1:
            if drawing:
                end_pos = clamp_to_canvas(mouse_pos)

                # сохраняем фигуру после отпускания мыши
                if current_tool not in (TOOL_PENCIL, TOOL_ERASER):
                    commit_shape(current_tool, start_pos, end_pos, current_color)

                drawing = False
                start_pos = None
                last_pos = None

        # движение мыши при рисовании
        if event.type == MOUSEMOTION and drawing:
            current_pos = clamp_to_canvas(mouse_pos)

            # рисование карандашом
            if current_tool == TOOL_PENCIL:
                if last_pos:
                    pygame.draw.line(
                        canvas,
                        current_color,
                        last_pos,
                        current_pos,
                        brush_size
                    )
                last_pos = current_pos

            # стирание ластиком
            elif current_tool == TOOL_ERASER:
                if last_pos:
                    pygame.draw.line(
                        canvas,
                        WHITE,
                        last_pos,
                        current_pos,
                        eraser_size
                    )
                last_pos = current_pos

    # рисует canvas
    DISPLAYSURF.blit(canvas, (0, 0))

    # показывает preview фигуры
    if drawing and start_pos and current_tool not in (TOOL_PENCIL, TOOL_ERASER):
        preview = canvas.copy()
        preview_pos = clamp_to_canvas(mouse_pos)
        draw_shape_preview(preview, current_tool, start_pos, preview_pos, current_color)
        DISPLAYSURF.blit(preview, (0, 0))

    # показывает круг ластика
    if current_tool == TOOL_ERASER and in_canvas:
        pygame.draw.circle(
            DISPLAYSURF,
            DARK_GRAY,
            mouse_pos,
            eraser_size // 2,
            1
        )

    # рисует нижнюю панель
    draw_toolbar()

    # обновляет экран
    pygame.display.update()