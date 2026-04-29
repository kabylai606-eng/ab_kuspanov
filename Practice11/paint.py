import pygame, sys, math
from pygame.locals import *

# Initialise pygame 
pygame.init()

# Constants 
SCREEN_WIDTH   = 900
SCREEN_HEIGHT  = 650
TOOLBAR_HEIGHT = 90

CANVAS_RECT = pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT - TOOLBAR_HEIGHT)

# Colors 
WHITE      = (255, 255, 255)
BLACK      = (0,   0,   0)
GRAY       = (200, 200, 200)
DARK_GRAY  = (100, 100, 100)
TOOLBAR_BG = (40,  40,  40)
HIGHLIGHT  = (180, 180, 255)

PALETTE = [
    (0,   0,   0),
    (255, 255, 255),
    (220, 50,  50),
    (50,  200, 50),
    (50,  50,  220),
    (255, 165, 0),
    (255, 255, 0),
    (160, 32,  240),
    (0,   220, 220),
    (255, 20,  147),
    (139, 69,  19),
    (128, 128, 128),
]

# Tool identifiers 
TOOL_PENCIL      = "pencil"
TOOL_RECTANGLE   = "rectangle"
TOOL_SQUARE      = "square"
TOOL_CIRCLE      = "circle"
TOOL_RIGHT_TRI   = "right_tri"
TOOL_EQUIL_TRI   = "equil_tri"
TOOL_RHOMBUS     = "rhombus"
TOOL_ERASER      = "eraser"

# Display 
DISPLAYSURF = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Paint – Practice 11")

# Persistent canvas 
canvas = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT - TOOLBAR_HEIGHT))
canvas.fill(WHITE)

# Fonts 
font_ui = pygame.font.SysFont("Verdana", 13)

# State 
current_tool  = TOOL_PENCIL
current_color = BLACK
brush_size    = 5
eraser_size   = 20
drawing       = False
start_pos     = None
last_pos      = None


# Geometry helpers 

def rect_from_drag(start, end):
    """Return (x, y, w, h) from two corner points (any order)."""
    x = min(start[0], end[0])
    y = min(start[1], end[1])
    w = abs(end[0] - start[0])
    h = abs(end[1] - start[1])
    return x, y, w, h


def square_from_drag(start, end):
    """
    Return (x, y, side) for a square.
    Uses the smaller of width/height to keep it square.
    """
    x, y, w, h = rect_from_drag(start, end)
    side = min(w, h)
    return x, y, side


def right_triangle_points(start, end):
    """
    Right-angle triangle:
      • right angle at bottom-left of the bounding box
      • vertical leg and horizontal leg
    """
    x, y, w, h = rect_from_drag(start, end)
    return [
        (x,     y + h),   # right-angle corner (bottom-left)
        (x,     y),       # top-left
        (x + w, y + h),   # bottom-right
    ]


def equilateral_triangle_points(start, end):
    """
    Equilateral triangle inscribed in the drag rectangle.
    Base at the bottom, apex at the top-centre.
    """
    x, y, w, h = rect_from_drag(start, end)
    base  = w
    apex  = (x + w // 2, y)
    bl    = (x,     y + h)
    br    = (x + w, y + h)
    return [apex, bl, br]


def rhombus_points(start, end):
    """
    Rhombus (diamond) using the four mid-points of the bounding rectangle.
    """
    x, y, w, h = rect_from_drag(start, end)
    return [
        (x + w // 2, y),        # top
        (x + w,      y + h // 2),  # right
        (x + w // 2, y + h),    # bottom
        (x,          y + h // 2),  # left
    ]


# Drawing helpers 

def draw_shape_preview(surface, tool, start, end, color):
    """Draw a temporary preview shape while the user drags."""
    if tool == TOOL_RECTANGLE:
        x, y, w, h = rect_from_drag(start, end)
        if w and h:
            pygame.draw.rect(surface, color, (x, y, w, h), 2)

    elif tool == TOOL_SQUARE:
        x, y, side = square_from_drag(start, end)
        if side:
            pygame.draw.rect(surface, color, (x, y, side, side), 2)

    elif tool == TOOL_CIRCLE:
        x, y, w, h = rect_from_drag(start, end)
        r = max(w, h) // 2
        cx = (start[0] + end[0]) // 2
        cy = (start[1] + end[1]) // 2
        if r:
            pygame.draw.circle(surface, color, (cx, cy), r, 2)

    elif tool == TOOL_RIGHT_TRI:
        pts = right_triangle_points(start, end)
        if len(pts) == 3:
            pygame.draw.polygon(surface, color, pts, 2)

    elif tool == TOOL_EQUIL_TRI:
        pts = equilateral_triangle_points(start, end)
        pygame.draw.polygon(surface, color, pts, 2)

    elif tool == TOOL_RHOMBUS:
        pts = rhombus_points(start, end)
        pygame.draw.polygon(surface, color, pts, 2)


def commit_shape(tool, start, end, color):
    """Permanently draw the finished shape onto the canvas."""
    if tool == TOOL_RECTANGLE:
        x, y, w, h = rect_from_drag(start, end)
        if w and h:
            pygame.draw.rect(canvas, color, (x, y, w, h))

    elif tool == TOOL_SQUARE:
        x, y, side = square_from_drag(start, end)
        if side:
            pygame.draw.rect(canvas, color, (x, y, side, side))

    elif tool == TOOL_CIRCLE:
        x, y, w, h = rect_from_drag(start, end)
        r  = max(w, h) // 2
        cx = (start[0] + end[0]) // 2
        cy = (start[1] + end[1]) // 2
        if r:
            pygame.draw.circle(canvas, color, (cx, cy), r)

    elif tool == TOOL_RIGHT_TRI:
        pts = right_triangle_points(start, end)
        pygame.draw.polygon(canvas, color, pts)

    elif tool == TOOL_EQUIL_TRI:
        pts = equilateral_triangle_points(start, end)
        pygame.draw.polygon(canvas, color, pts)

    elif tool == TOOL_RHOMBUS:
        pts = rhombus_points(start, end)
        pygame.draw.polygon(canvas, color, pts)


# Toolbar layout 

TOOLS_ROW1 = [
    (TOOL_PENCIL,    "Pencil"),
    (TOOL_RECTANGLE, "Rect"),
    (TOOL_SQUARE,    "Square"),
    (TOOL_CIRCLE,    "Circle"),
]
TOOLS_ROW2 = [
    (TOOL_RIGHT_TRI, "R.Tri"),
    (TOOL_EQUIL_TRI, "Eq.Tri"),
    (TOOL_RHOMBUS,   "Rhombus"),
    (TOOL_ERASER,    "Eraser"),
]

BTN_W = 80
BTN_H = 26


def tb_y():
    return SCREEN_HEIGHT - TOOLBAR_HEIGHT


def tool_btn_rect(row, col):
    return pygame.Rect(10 + col * (BTN_W + 5), tb_y() + 8 + row * (BTN_H + 6), BTN_W, BTN_H)


def swatch_rect(index):
    start_x = 10 + 4 * (BTN_W + 5) + 10
    return pygame.Rect(start_x + index * 34, tb_y() + 8, 30, 30)


def draw_toolbar():
    """Render the full toolbar."""
    pygame.draw.rect(DISPLAYSURF, TOOLBAR_BG, (0, tb_y(), SCREEN_WIDTH, TOOLBAR_HEIGHT))

    # Draw tool buttons in two rows
    for row_idx, row in enumerate([TOOLS_ROW1, TOOLS_ROW2]):
        for col_idx, (tool_id, label) in enumerate(row):
            rect  = tool_btn_rect(row_idx, col_idx)
            color = HIGHLIGHT if tool_id == current_tool else GRAY
            pygame.draw.rect(DISPLAYSURF, color, rect, border_radius=4)
            pygame.draw.rect(DISPLAYSURF, DARK_GRAY, rect, 1, border_radius=4)
            lbl = font_ui.render(label, True, BLACK)
            DISPLAYSURF.blit(lbl, lbl.get_rect(center=rect.center))

    # Color palette swatches
    for i, col in enumerate(PALETTE):
        sw = swatch_rect(i)
        pygame.draw.rect(DISPLAYSURF, col, sw)
        border = (255, 255, 0) if col == current_color else DARK_GRAY
        pygame.draw.rect(DISPLAYSURF, border, sw, 2)

    # Active color label
    start_x = 10 + 4 * (BTN_W + 5) + 10
    prev_r  = pygame.Rect(start_x, tb_y() + 44, 30 + (len(PALETTE) - 1) * 34, 20)
    pygame.draw.rect(DISPLAYSURF, current_color, prev_r)
    lbl = font_ui.render("Active color", True,
                         WHITE if sum(current_color) < 380 else BLACK)
    DISPLAYSURF.blit(lbl, lbl.get_rect(center=prev_r.center))


def handle_toolbar_click(pos):
    """Update tool or color based on toolbar click position."""
    global current_tool, current_color

    for row_idx, row in enumerate([TOOLS_ROW1, TOOLS_ROW2]):
        for col_idx, (tool_id, _) in enumerate(row):
            if tool_btn_rect(row_idx, col_idx).collidepoint(pos):
                current_tool = tool_id
                return

    for i, col in enumerate(PALETTE):
        if swatch_rect(i).collidepoint(pos):
            current_color = col
            return


# Main loop 
clock = pygame.time.Clock()

while True:
    clock.tick(60)
    mouse_pos = pygame.mouse.get_pos()
    in_canvas = CANVAS_RECT.collidepoint(mouse_pos)

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            if in_canvas:
                drawing   = True
                start_pos = mouse_pos
                last_pos  = mouse_pos
            else:
                handle_toolbar_click(mouse_pos)

        if event.type == MOUSEBUTTONUP and event.button == 1:
            if drawing:
                # Commit shape tools on release
                if current_tool not in (TOOL_PENCIL, TOOL_ERASER):
                    commit_shape(current_tool, start_pos, mouse_pos, current_color)
                drawing   = False
                start_pos = None
                last_pos  = None

        if event.type == MOUSEMOTION and drawing and in_canvas:
            if current_tool == TOOL_PENCIL:
                if last_pos:
                    pygame.draw.line(canvas, current_color,
                                     last_pos, mouse_pos, brush_size)
                last_pos = mouse_pos
            elif current_tool == TOOL_ERASER:
                if last_pos:
                    pygame.draw.line(canvas, WHITE,
                                     last_pos, mouse_pos, eraser_size)
                last_pos = mouse_pos

    # Render 
    DISPLAYSURF.blit(canvas, (0, 0))

    # Live preview for shape tools while dragging
    if drawing and start_pos and current_tool not in (TOOL_PENCIL, TOOL_ERASER):
        preview = canvas.copy()
        draw_shape_preview(preview, current_tool, start_pos, mouse_pos, current_color)
        DISPLAYSURF.blit(preview, (0, 0))

    # Show eraser cursor circle
    if current_tool == TOOL_ERASER and in_canvas:
        pygame.draw.circle(DISPLAYSURF, DARK_GRAY, mouse_pos, eraser_size // 2, 1)

    draw_toolbar()
    pygame.display.update()