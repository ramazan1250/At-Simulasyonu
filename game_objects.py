# game_objects.py
import pygame
import config as cfg

class Projectile:
    """Represents the projectile (circle) in the simulation."""
    def __init__(self, initial_pos_px=None):
        self.radius = cfg.CIRCLE_RADIUS_PX
        self.color = cfg.YELLOW
        # Use provided initial position or default from config
        if initial_pos_px is None:
            self.initial_pos_px = list(cfg.INITIAL_CIRCLE_POS_PX)
        else:
            self.initial_pos_px = list(initial_pos_px)
        # Current position starts at the initial position
        self.current_pos_px = list(self.initial_pos_px)

    def set_initial_position(self, pos_px):
        """Sets both initial and current position."""
        self.initial_pos_px = list(pos_px)
        self.current_pos_px = list(pos_px)

    def reset_to_initial(self):
        """Resets the current position to the initial position."""
        self.current_pos_px = list(self.initial_pos_px)

    def update_position(self, new_pos_px):
        """Updates the current position."""
        self.current_pos_px = list(new_pos_px)

    def draw(self, surface):
        """Draws the projectile on the given surface."""
        center_x_int = int(self.current_pos_px[0])
        center_y_int = int(self.current_pos_px[1])
        # Basic bounds check before drawing
        if 0 <= center_x_int <= cfg.WIDTH and 0 <= center_y_int <= cfg.HEIGHT:
            pygame.draw.circle(surface, self.color, (center_x_int, center_y_int), self.radius)


class Target:
    """Represents the target box in the simulation."""
    def __init__(self, initial_pos_px=None):
        self.width = cfg.BOX_WIDTH_PX
        self.height = cfg.BOX_HEIGHT_PX
        self.color = cfg.RED
        # Use provided initial position or default from config
        if initial_pos_px is None:
            self.pos_px = list(cfg.INITIAL_BOX_POS_PX)
        else:
            self.pos_px = list(initial_pos_px)
        # Rect object for drawing and collision detection (optional)
        self.rect = pygame.Rect(self.pos_px[0], self.pos_px[1], self.width, self.height)

    def set_position(self, pos_px):
        """Sets the target's top-left position."""
        self.pos_px = list(pos_px)
        self.rect.topleft = self.pos_px

    @property
    def center_pos_px(self):
        """Returns the center position of the target."""
        return [self.pos_px[0] + self.width / 2, self.pos_px[1] + self.height / 2]

    def draw(self, surface):
        """Draws the target box on the given surface."""
        # Update rect position just in case it was changed directly (though set_position is preferred)
        self.rect.topleft = (int(self.pos_px[0]), int(self.pos_px[1]))
        pygame.draw.rect(surface, self.color, self.rect)