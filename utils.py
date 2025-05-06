# utils.py
import pygame
import math
import config as cfg

# --- Unit Conversion ---
def px_to_m(pixels):
    """Converts pixels to meters."""
    if cfg.PIXELS_PER_METER == 0: return 0.0 # Avoid division by zero
    return pixels / cfg.PIXELS_PER_METER

def m_to_px(meters):
    """Converts meters to pixels."""
    return meters * cfg.PIXELS_PER_METER

def px_s_to_mps(pixels_per_second):
    """Converts pixels per second to meters per second."""
    if cfg.PIXELS_PER_METER == 0: return 0.0 # Avoid division by zero
    return pixels_per_second / cfg.PIXELS_PER_METER

def mps_to_px_s(meters_per_second):
    """Converts meters per second to pixels per second."""
    return meters_per_second * cfg.PIXELS_PER_METER

# --- Drawing Helpers ---
def draw_text(text, text_font, color, surface, x, y, center=False, topright=False):
    """Renders and draws text onto a surface."""
    if not text_font:
        print(f"Error: Font not loaded or invalid for text '{text}'")
        return # Cannot render without a valid font
    try:
        textobj = text_font.render(text, True, color)
        textrect = textobj.get_rect()
        if center:
            textrect.center = (int(x), int(y))
        elif topright:
            textrect.topright = (int(x), int(y))
        else:
            textrect.topleft = (int(x), int(y))
        surface.blit(textobj, textrect)
    except Exception as e:
        print(f"Error rendering or blitting text '{text}': {e}")
        pass # Optionally, draw placeholder text or log differently

def draw_arrow(surface, color, start, end, arrow_size):
    """Draws a line with an arrowhead at the end."""
    line_thickness = cfg.DRAW_ARROW_LINE_THICKNESS
    try:
        start_int = (int(start[0]), int(start[1]))
        end_int = (int(end[0]), int(end[1]))
        pygame.draw.line(surface, color, start_int, end_int, line_thickness)
    except Exception as e:
        print(f"Error drawing line from {start} to {end}: {e}")
        return # Don't proceed if line fails

    try:
        # Calculate angle only if start and end are different
        if start_int == end_int: return # No arrowhead for zero-length line
        angle = math.atan2(start_int[1] - end_int[1], start_int[0] - end_int[0])

        # Calculate arrowhead points
        p1x = end_int[0] + arrow_size * math.cos(angle + math.pi / 6)
        p1y = end_int[1] + arrow_size * math.sin(angle + math.pi / 6)
        p2x = end_int[0] + arrow_size * math.cos(angle - math.pi / 6)
        p2y = end_int[1] + arrow_size * math.sin(angle - math.pi / 6)

        # Draw the arrowhead polygon
        pygame.draw.polygon(surface, color, (end_int, (int(p1x), int(p1y)), (int(p2x), int(p2y))))
    except (ValueError, OverflowError, TypeError, ZeroDivisionError) as e:
        # Handle potential math errors or invalid points
        print(f"Could not draw arrowhead for arrow from {start} to {end}: {e}")
        pass