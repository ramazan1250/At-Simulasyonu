# physics.py
import config as cfg
import math

class PhysicsEngine:
    """Handles projectile motion calculations."""

    def __init__(self):
        self.gravity_px_s2 = cfg.GRAVITY_PX_PER_SEC2

    def calculate_required_velocities(self, initial_pos_px, target_center_px, time_to_target_sec):
        """
        Calculates the initial velocities (px/s) required for the projectile
        to reach the target center in the given time.

        Args:
            initial_pos_px (list): Projectile's starting [x, y] in pixels.
            target_center_px (list): Target's center [x, y] in pixels.
            time_to_target_sec (float): The desired time to reach the target.

        Returns:
            tuple: (v0x_px_s, v0y_px_s) required initial velocities in pixels/sec.
                   Returns (0, 0) if time_to_target_sec is zero or negative.
        """
        if time_to_target_sec <= 0:
            return 0.0, 0.0

        delta_x_px = target_center_px[0] - initial_pos_px[0]
        # Delta Y in physics coordinates (relative vertical distance, positive if target is higher physics-wise)
        delta_y_physics_px = initial_pos_px[1] - target_center_px[1] # Correct calculation

        # x = v0x * t  => v0x = x / t
        v0x_px_s = delta_x_px / time_to_target_sec

        # Physics: DeltaY = v0y_physics * t - 0.5 * g * t^2
        # v0y_physics = (DeltaY + 0.5 * g * t^2) / t
        # Note: Use gravity_px_s2 (positive value) here. The sign comes from the equation structure.
        try:
            v0y_physics_px_s = (delta_y_physics_px + 0.5 * self.gravity_px_s2 * time_to_target_sec**2) / time_to_target_sec
        except ZeroDivisionError:
             # This case is already handled by the initial check for time_to_target_sec <= 0
             # But adding it defensively.
             return 0.0, 0.0

        # Convert v0y from physics (up positive) to pygame (down positive)
        v0y_px_s = -v0y_physics_px_s

        return v0x_px_s, v0y_px_s

    def calculate_kinematic_update(self, initial_pos_px, v0x_px_s, v0y_px_s, t_elapsed_effective):
        """
        Calculates the projectile's position and velocity at a given effective time.

        Args:
            initial_pos_px (list): Projectile's starting [x, y] in pixels.
            v0x_px_s (float): Initial horizontal velocity in pixels/sec.
            v0y_px_s (float): Initial vertical velocity in pixels/sec (Pygame coords).
            t_elapsed_effective (float): The effective elapsed simulation time in seconds.

        Returns:
            tuple: (new_pos_px, current_v_px_s) where
                   new_pos_px is the calculated [x, y] position,
                   current_v_px_s is the current [vx, vy] velocity in pixels/sec.
        """
        # Calculate new position
        pos_x = initial_pos_px[0] + v0x_px_s * t_elapsed_effective
        # v0y_px_s is negative for upward launch in Pygame coords. Gravity (gravity_px_s2) is positive (down).
        pos_y = initial_pos_px[1] + v0y_px_s * t_elapsed_effective + 0.5 * self.gravity_px_s2 * t_elapsed_effective**2

        # Calculate current velocity
        vx = v0x_px_s
        vy = v0y_px_s + self.gravity_px_s2 * t_elapsed_effective

        return [pos_x, pos_y], [vx, vy]