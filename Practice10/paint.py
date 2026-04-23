import pygame, sys
from pygame.locals import *

pygame.init()

SCREEN_WIDTH  = 800
SCREEN_HEIGHT = 600
TOOLBAR_HEIGHT = 80   # height of the bottom toolbar

# Drawing area 
CANVAS_RECT = pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT - TOOLBAR_HEIGHT)


WHITE   = (255, 255, 255)
BLACK   = (0,   0,   0)
GRAY    = (200, 200, 200)
DARK_GRAY = (100, 100, 100)
TOOLBAR_BG = (50, 50, 50)

# Palette of selectable colors
PALETTE = [
    (0,   0,   0),     # Black
    (255, 255, 255),   # White
    (255, 0,   0),     # Red
    (0,   200, 0),     # Green
    (0,   0,   255),   # Blue
    (255, 165, 0),     # Orange
    (255, 255, 0),     # Yellow
    (160, 32,  240),   # Purple
    (0,   255, 255),   # Cyan
    (255, 20,  147),   # Pink
    (139, 69,  19),    # Brown
    (128, 128, 128),   # Gray
]

# Tool identifiers
TOOL_PENCIL    = "pencil"
TOOL_RECTANGLE = "rectangle"
TOOL_CIRCLE    = "circle"
TOOL_ERASER    = "eraser"

# Display 
DISPLAYSURF = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Paint – Practice 10")

# Canvas surface (persistent drawing) 
canvas = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT - TOOLBAR_HEIGHT))
canvas.fill(WHITE)

# Fonts 
font_ui = pygame.font.SysFont("Verdana", 14)

# State variables 
current_tool  = TOOL_PENCIL
current_color = BLACK
brush_size    = 5
eraser_size   = 20

drawing       = False     # True while mouse button is held
start_pos     = None      # starting position of a drag (rect / circle)
last_pos      = None      # last position for pencil/eraser free-draw


# UI layout helpers 

def toolbar_y():
    """Y coordinate where the toolbar starts."""
    return SCREEN_HEIGHT - TOOLBAR_HEIGHT


def draw_toolbar():
    """Render the bottom toolbar with tool buttons, palette, and labels."""
    tb_rect = pygame.Rect(0, toolbar_y(), SCREEN_WIDTH, TOOLBAR_HEIGHT)
    pygame.draw.rect(DISPLAYSURF, TOOLBAR_BG, tb_rect)

    # Tool buttons 
    tools = [
        (TOOL_PENCIL,    "Pencil"),
        (TOOL_RECTANGLE, "Rect"),
        (TOOL_CIRCLE,    "Circle"),
        (TOOL_ERASER,    "Eraser"),
    ]

    btn_x = 10
    for tool_id, label in tools:
        btn_rect = pygame.Rect(btn_x, toolbar_y() + 10, 70, 28)
        # Highlight active tool
        color = (180, 180, 255) if tool_id == current_tool else GRAY
        pygame.draw.rect(DISPLAYSURF, color, btn_rect, border_radius=4)
        pygame.draw.rect(DISPLAYSURF, DARK_GRAY, btn_rect, 1, border_radius=4)
        lbl = font_ui.render(label, True, BLACK)
        DISPLAYSURF.blit(lbl, lbl.get_rect(center=btn_rect.center))
        btn_x += 80

    # Color palette 
    swatch_x = btn_x + 10
    for i, col in enumerate(PALETTE):
        sw = pygame.Rect(swatch_x + i * 34, toolbar_y() + 10, 30, 30)
        pygame.draw.rect(DISPLAYSURF, col, sw)
        # Highlight selected color
        border_color = (255, 255, 0) if col == current_color else DARK_GRAY
        pygame.draw.rect(DISPLAYSURF, border_color, sw, 2)

    # Current color preview 
    preview_rect = pygame.Rect(swatch_x, toolbar_y() + 46, 30 + (len(PALETTE) - 1) * 34, 22)
    pygame.draw.rect(DISPLAYSURF, current_color, preview_rect)
    lbl = font_ui.render("Active color", True, WHITE if sum(current_color) < 380 else BLACK)
    DISPLAYSURF.blit(lbl, lbl.get_rect(center=preview_rect.center))


def get_tool_button_rect(index):
    """Return the rect for the tool button at the given index."""
    return pygame.Rect(10 + index * 80, toolbar_y() + 10, 70, 28)


def get_swatch_rect(index):
    """Return the rect for the palette swatch at the given index."""
    btn_x = 10 + 4 * 80 + 10   # after tool buttons
    return pygame.Rect(btn_x + index * 34, toolbar_y() + 10, 30, 30)


def handle_toolbar_click(pos):
    """Detect clicks on tool buttons or color swatches and update state."""
    global current_tool, current_color

    tools = [TOOL_PENCIL, TOOL_RECTANGLE, TOOL_CIRCLE, TOOL_ERASER]
    for i, tool_id in enumerate(tools):
        if get_tool_button_rect(i).collidepoint(pos):
            current_tool = tool_id
            return

    for i, col in enumerate(PALETTE):
        if get_swatch_rect(i).collidepoint(pos):
            current_color = col
            return


# Drawing helpers
def draw_preview(surface, tool, start, end, color, size):
    """Draw a temporary shape preview while the user is dragging."""
    if tool == TOOL_RECTANGLE:
        rx = min(start[0], end[0])
        ry = min(start[1], end[1])
        rw = abs(end[0] - start[0])
        rh = abs(end[1] - start[1])
        pygame.draw.rect(surface, color, (rx, ry, rw, rh), 2)

    elif tool == TOOL_CIRCLE:
        cx = (start[0] + end[0]) // 2
        cy = (start[1] + end[1]) // 2
        r  = max(abs(end[0] - start[0]), abs(end[1] - start[1])) // 2
        if r > 0:
            pygame.draw.circle(surface, color, (cx, cy), r, 2)


def commit_shape(tool, start, end, color, size):
    """Permanently draw the finalized shape onto the canvas."""
    if tool == TOOL_RECTANGLE:
        rx = min(start[0], end[0])
        ry = min(start[1], end[1])
        rw = abs(end[0] - start[0])
        rh = abs(end[1] - start[1])
        if rw > 0 and rh > 0:
            pygame.draw.rect(canvas, color, (rx, ry, rw, rh))
            pygame.draw.rect(canvas, color, (rx, ry, rw, rh), 2)

    elif tool == TOOL_CIRCLE:
        cx = (start[0] + end[0]) // 2
        cy = (start[1] + end[1]) // 2
        r  = max(abs(end[0] - start[0]), abs(end[1] - start[1])) // 2
        if r > 0:
            pygame.draw.circle(canvas, color, (cx, cy), r)


# Main loop 
clock = pygame.time.Clock()

while True:
    clock.tick(60)
    mouse_pos = pygame.mouse.get_pos()

    # Is the mouse inside the canvas (above toolbar)?
    in_canvas = CANVAS_RECT.collidepoint(mouse_pos)

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

        # Mouse button pressed 
        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            if in_canvas:
                drawing   = True
                start_pos = mouse_pos
                last_pos  = mouse_pos
            else:
                # Click on toolbar
                handle_toolbar_click(mouse_pos)

        # Mouse button released
        if event.type == MOUSEBUTTONUP and event.button == 1:
            if drawing:
                if current_tool in (TOOL_RECTANGLE, TOOL_CIRCLE):
                    commit_shape(current_tool, start_pos, mouse_pos,
                                 current_color, brush_size)
                drawing   = False
                start_pos = None
                last_pos  = None

        # Mouse motion (pencil / eraser free draw) 
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
    # Draw the persistent canvas to the screen
    DISPLAYSURF.blit(canvas, (0, 0))

    # Draw real-time shape preview (rectangle / circle while dragging)
    if drawing and start_pos and current_tool in (TOOL_RECTANGLE, TOOL_CIRCLE):
        preview = canvas.copy()
        draw_preview(preview, current_tool, start_pos, mouse_pos,
                     current_color, brush_size)
        DISPLAYSURF.blit(preview, (0, 0))

    # Draw eraser cursor outline
    if current_tool == TOOL_ERASER and in_canvas:
        pygame.draw.circle(DISPLAYSURF, DARK_GRAY, mouse_pos, eraser_size // 2, 1)

    # Draw the toolbar on top
    draw_toolbar()

    pygame.display.update()