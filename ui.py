# ui.py
import pygame
import config as cfg
import utils # For drawing text, arrows, conversions
import math

class UIManager:
    """Manages UI elements, state, drawing, and interactions."""

    def __init__(self, screen, scene_config):
        self.screen = screen
        self.scene_config = scene_config
        self.scene_title = self.scene_config.get("title", "Atış Simülasyonu")
        # Get explicitly enabled sliders for this scene
        self.sliders_enabled = self.scene_config.get("sliders_enabled", []) # Use empty list if none specified

        # Load fonts
        self.font_large = pygame.font.Font(None, cfg.FONT_SIZE_LARGE)
        self.font_medium = pygame.font.Font(None, cfg.FONT_SIZE_MEDIUM)
        self.font_small = pygame.font.Font(None, cfg.FONT_SIZE_SMALL)
        self.font_formula = pygame.font.Font(None, cfg.FONT_SIZE_FORMULA)
        self.font_title = pygame.font.Font(None, cfg.FONT_SIZE_SMALL) # Font for title
        self.font_back_button = pygame.font.Font(None, cfg.FONT_SIZE_SMALL) # Font for back button

        # --- UI State ---
        self.sliders = {}
        self.dragging_slider = None
        self.input_active = False
        self.input_error = False
        self.error_message = None # Added for specific error messages
        self.time_to_target_str = self.scene_config.get("default_time_str", "2.0")
        # Vector display toggles (managed by UI)
        self.show_vectors = True
        self.show_velocity_vector = False
        self.show_acceleration_vector = False

        # --- UI Element Rects ---
        # Define ALL potential slider rects first, even if not enabled for this scene
        self._define_all_slider_rects()
        # Define other control rects
        self._define_control_rects()
        # Define back button relative to sliders (use circle_y if possible)
        # PASS self.sliders_enabled so it knows which sliders are active
        self._define_back_button_rect(self.sliders_enabled)


    def _define_all_slider_rects(self):
        """Defines the rectangles for ALL potential sliders."""
        self.slider_rects_track = {
            "circle_x": pygame.Rect(cfg.SLIDER_X_OFFSET, cfg.SLIDER_AREA_Y_START, cfg.SLIDER_TRACK_WIDTH, cfg.SLIDER_TRACK_HEIGHT),
            "circle_y": pygame.Rect(cfg.SLIDER_X_OFFSET, cfg.SLIDER_AREA_Y_START + cfg.SLIDER_Y_SPACING, cfg.SLIDER_TRACK_WIDTH, cfg.SLIDER_TRACK_HEIGHT),
            "box_x": pygame.Rect(cfg.WIDTH - cfg.SLIDER_TRACK_WIDTH - cfg.SLIDER_X_OFFSET, cfg.SLIDER_AREA_Y_START, cfg.SLIDER_TRACK_WIDTH, cfg.SLIDER_TRACK_HEIGHT),
            "box_y": pygame.Rect(cfg.WIDTH - cfg.SLIDER_TRACK_WIDTH - cfg.SLIDER_X_OFFSET, cfg.SLIDER_AREA_Y_START + cfg.SLIDER_Y_SPACING, cfg.SLIDER_TRACK_WIDTH, cfg.SLIDER_TRACK_HEIGHT),
        }

    def _define_control_rects(self):
        """Defines rectangles for buttons, input box etc."""
        # Bottom Controls (Centered)
        self.input_box_rect = pygame.Rect(cfg.CONTROLS_START_X, cfg.CONTROL_AREA_Y_START + cfg.INPUT_BOX_Y_OFFSET, cfg.TEXT_BOX_WIDTH, cfg.TEXT_BOX_HEIGHT)
        self.launch_button_rect = pygame.Rect(self.input_box_rect.right + cfg.SPACING_PX, cfg.CONTROL_AREA_Y_START, cfg.BUTTON_WIDTH, cfg.BUTTON_HEIGHT)
        self.restart_button_rect = pygame.Rect(self.launch_button_rect.right + cfg.SPACING_PX, cfg.CONTROL_AREA_Y_START, cfg.BUTTON_WIDTH, cfg.BUTTON_HEIGHT)
        self.toggle_vec_vis_button_rect = pygame.Rect(self.restart_button_rect.right + cfg.SPACING_PX, cfg.CONTROL_AREA_Y_START, cfg.TOGGLE_VEC_VIS_BUTTON_WIDTH, cfg.BUTTON_HEIGHT)
        self.toggle_vec_mode_button_rect = pygame.Rect(self.toggle_vec_vis_button_rect.right + cfg.SPACING_PX, cfg.CONTROL_AREA_Y_START, cfg.TOGGLE_VEC_MODE_BUTTON_WIDTH, cfg.BUTTON_HEIGHT)
        self.toggle_vec_type_button_rect = pygame.Rect(self.toggle_vec_mode_button_rect.right + cfg.SPACING_PX, cfg.CONTROL_AREA_Y_START, cfg.TOGGLE_VEC_TYPE_BUTTON_WIDTH, cfg.BUTTON_HEIGHT)
        # Formula Area Controls
        self.speed_minus_button_rect = pygame.Rect(cfg.WIDTH // 2 - cfg.SPEED_MINUS_X_OFFSET, cfg.FORMULA_CONTROLS_Y_OFFSET, cfg.SMALL_BUTTON_WIDTH, cfg.SMALL_BUTTON_HEIGHT)
        self.speed_plus_button_rect = pygame.Rect(cfg.WIDTH // 2 + cfg.SPEED_PLUS_X_OFFSET, cfg.FORMULA_CONTROLS_Y_OFFSET, cfg.SMALL_BUTTON_WIDTH, cfg.SMALL_BUTTON_HEIGHT)
        self.pause_button_rect = pygame.Rect(self.speed_minus_button_rect.left - cfg.PAUSE_BUTTON_WIDTH - cfg.SPACING_PX, cfg.FORMULA_CONTROLS_Y_OFFSET, cfg.PAUSE_BUTTON_WIDTH, cfg.BUTTON_HEIGHT)


    def _define_back_button_rect(self, enabled_sliders): # Pass enabled sliders
        """Defines the back button rect relative to the circle_y slider track if it is enabled."""
        # Default position if circle_y slider is not enabled or doesn't exist
        default_x = cfg.PADDING_PX
        default_y = cfg.SLIDER_AREA_Y_START + cfg.SLIDER_Y_SPACING + cfg.SLIDER_TRACK_HEIGHT + cfg.BACK_BUTTON_Y_OFFSET_AFTER_SLIDER # Place below where second slider would be

        back_button_x = default_x
        back_button_y = default_y

        # Check if 'circle_y' slider is enabled for the current scene
        if "circle_y" in enabled_sliders:
            circle_y_track = self.slider_rects_track.get("circle_y")
            if circle_y_track:
                # Position below the circle_y slider's track using the offset from config
                back_button_x = circle_y_track.left # Align with the left of the slider track
                back_button_y = circle_y_track.bottom + cfg.BACK_BUTTON_Y_OFFSET_AFTER_SLIDER
            # else: Use default if rect somehow not found (shouldn't happen)
        # else: Use default position because circle_y is not enabled

        self.back_button_rect = pygame.Rect(
            back_button_x,
            back_button_y,
            cfg.BACK_BUTTON_WIDTH,
            cfg.BACK_BUTTON_HEIGHT
        )

    def initialize_sliders(self, projectile, target):
         """Calculates initial slider values based on object positions for ENABLED sliders."""
         drawable_height = cfg.DRAWABLE_HEIGHT
         y_offset = cfg.DRAWABLE_Y_OFFSET
         if not projectile or not target: return
         sliders_temp = {}
         try:
             # Calculate ranges needed for potentially enabled sliders
             circle_range_x = cfg.WIDTH - 2 * projectile.radius
             circle_range_y = drawable_height - 2 * projectile.radius
             box_range_x = cfg.WIDTH - target.width
             box_range_y = drawable_height - target.height

             # Calculate values only for the sliders enabled in this scene
             if "circle_x" in self.sliders_enabled:
                 sliders_temp["circle_x"] = (projectile.initial_pos_px[0] - projectile.radius) / circle_range_x if circle_range_x > 0 else 0.5
             if "circle_y" in self.sliders_enabled:
                 sliders_temp["circle_y"] = (projectile.initial_pos_px[1] - y_offset - projectile.radius) / circle_range_y if circle_range_y > 0 else 0.5
             if "box_x" in self.sliders_enabled:
                 sliders_temp["box_x"] = target.pos_px[0] / box_range_x if box_range_x > 0 else 0.5
             if "box_y" in self.sliders_enabled:
                  # Use target's top-left for box_y slider mapping
                 sliders_temp["box_y"] = (target.pos_px[1] - y_offset) / box_range_y if box_range_y > 0 else 0.5

         except (AttributeError, IndexError, TypeError, ZeroDivisionError) as e:
             print(f"Error calculating initial slider values: {e}")
             # Provide default values for enabled sliders if calculation fails
             for key in self.sliders_enabled:
                 sliders_temp[key] = 0.5

         # Store clamped values for enabled sliders
         self.sliders = {k: max(0.0, min(1.0, sliders_temp.get(k, 0.5))) for k in self.sliders_enabled}


    def get_slider_handle_rect(self, slider_key):
        """Calculates the rectangle for a slider's handle."""
        # Check if this slider is actually enabled for the current scene
        if slider_key not in self.sliders_enabled:
            return None # Do not calculate or draw if not enabled
        # Check if track rect exists (safety)
        if slider_key not in self.slider_rects_track:
             return None

        track_rect = self.slider_rects_track[slider_key]
        slider_val = self.sliders.get(slider_key, 0.5) # Get current value (0-1)
        slider_val = max(0.0, min(1.0, slider_val)) # Clamp value

        # Calculate handle position based on value
        # Use track_rect.width - cfg.SLIDER_HANDLE_WIDTH as the effective range for the handle's left edge
        effective_track_width = track_rect.width - cfg.SLIDER_HANDLE_WIDTH
        handle_x = track_rect.left + slider_val * effective_track_width
        handle_y = track_rect.centery - cfg.SLIDER_HANDLE_HEIGHT // 2

        # Clamp handle position (redundant due to calculation method, but safe)
        handle_x = max(track_rect.left, min(handle_x, track_rect.right - cfg.SLIDER_HANDLE_WIDTH))

        return pygame.Rect(handle_x, handle_y, cfg.SLIDER_HANDLE_WIDTH, cfg.SLIDER_HANDLE_HEIGHT)


    def handle_event(self, event, simulation_running, simulation_paused):
        """Processes a single Pygame event and updates UI state."""
        action = None
        mouse_pos = pygame.mouse.get_pos()

        # Check Back Button First
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.back_button_rect.collidepoint(mouse_pos):
                return "back_to_menu"

        # Handle Slider Interactions (Only if sliders are enabled for the scene)
        if self.sliders_enabled: # Optimization: Only check sliders if there are any enabled
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.dragging_slider = None
                for key in self.sliders_enabled: # Only check enabled sliders
                    track_rect = self.slider_rects_track.get(key)
                    handle_rect = self.get_slider_handle_rect(key) # This now returns None if not enabled
                    if track_rect and handle_rect: # Check if rects exist
                        # Allow clicking on track or handle
                        clickable_area = track_rect.inflate(0, cfg.SLIDER_HANDLE_HEIGHT) # Make track easier to click vertically
                        if clickable_area.collidepoint(mouse_pos):
                            self.dragging_slider = key
                            # Update value immediately if track clicked
                            # Adjust calculation for effective width
                            effective_track_width = track_rect.width - cfg.SLIDER_HANDLE_WIDTH
                            if effective_track_width > 0:
                               raw_val = (mouse_pos[0] - track_rect.left - cfg.SLIDER_HANDLE_WIDTH / 2) / effective_track_width
                            else:
                               raw_val = 0.5 # Avoid division by zero if track too small
                            self.sliders[key] = max(0.0, min(1.0, raw_val))
                            action = "update_slider"
                            break # Found slider, stop checking
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.dragging_slider = None
            elif event.type == pygame.MOUSEMOTION and self.dragging_slider is not None:
                # Ensure the dragged slider is actually enabled for this scene
                if self.dragging_slider in self.sliders_enabled:
                    track_rect = self.slider_rects_track[self.dragging_slider]
                    # Adjust calculation for effective width
                    effective_track_width = track_rect.width - cfg.SLIDER_HANDLE_WIDTH
                    if effective_track_width > 0:
                        raw_val = (mouse_pos[0] - track_rect.left - cfg.SLIDER_HANDLE_WIDTH / 2) / effective_track_width
                    else:
                        raw_val = 0.5
                    self.sliders[self.dragging_slider] = max(0.0, min(1.0, raw_val))
                    action = "update_slider"
                else: # Should not happen if logic is correct, but safety check
                    self.dragging_slider = None

        # Handle Button / Input Box Interactions (only if not dragging slider)
        if self.dragging_slider is None:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Input Box Activation
                self.input_active = self.input_box_rect.collidepoint(mouse_pos)
                if self.input_active:
                    self.input_error = False; self.error_message = None

                # Button Clicks
                if self.launch_button_rect.collidepoint(mouse_pos) and not simulation_running: action = "launch"
                elif self.restart_button_rect.collidepoint(mouse_pos): action = "reset"
                elif self.toggle_vec_vis_button_rect.collidepoint(mouse_pos): self.show_vectors = not self.show_vectors
                elif self.toggle_vec_mode_button_rect.collidepoint(mouse_pos): self.show_velocity_vector = not self.show_velocity_vector
                elif self.toggle_vec_type_button_rect.collidepoint(mouse_pos): self.show_acceleration_vector = not self.show_acceleration_vector
                elif self.speed_minus_button_rect.collidepoint(mouse_pos): action = "speed_down"
                elif self.speed_plus_button_rect.collidepoint(mouse_pos): action = "speed_up"
                elif self.pause_button_rect.collidepoint(mouse_pos) and (simulation_running or simulation_paused): # Allow toggle even if finished but was running
                    action = "pause_toggle"

            # Keyboard Input for Active Input Box
            elif event.type == pygame.KEYDOWN and self.input_active:
                active_scene_name = self.scene_config.get("title", "") # Get scene name for context
                if event.key == pygame.K_RETURN:
                    self.input_active = False
                    # Trigger action based on scene type after Enter
                    if active_scene_name.startswith("Yatay Atış"):
                        action = "launch" # Yatay calculates time, so Enter launches
                    elif active_scene_name.startswith("Dikey Atış"):
                         action = "launch" # Dikey uses input time, Enter launches
                    else: # Default (Eğik Atış etc.)
                        action = "validate_time" # Other scenes validate time first
                elif event.key == pygame.K_BACKSPACE:
                    self.time_to_target_str = self.time_to_target_str[:-1]
                    self.input_error = False; self.error_message = None
                elif event.unicode.isdigit() or (event.unicode == '.' and '.' not in self.time_to_target_str):
                     self.time_to_target_str += event.unicode
                     self.input_error = False; self.error_message = None

        return action


    def validate_time_input(self):
        """Validates the content of time_to_target_str. Returns valid float or None."""
        try:
            time_input = float(self.time_to_target_str)
            if time_input > 0:
                self.input_error = False; self.error_message = None
                return time_input
            else:
                self.input_error = True; self.error_message = "Süre > 0 olmalı"
                return None
        except ValueError:
            self.input_error = True; self.error_message = "Geçersiz süre formatı"
            return None

    def draw_all(self, game_state):
        """Draws all UI elements based on the provided game state."""
        self.screen.fill(cfg.BLUE)
        self.draw_scene_title(game_state.get('scene_title', '')) # Draw scene title first
        self.draw_formulas(game_state)
        self.draw_formula_controls(game_state['simulation_paused'], game_state['simulation_speed_multiplier'])
        self.draw_separator()
        # Draw sliders only if they are enabled for the scene
        if self.sliders_enabled:
            self.draw_sliders(game_state['projectile'], game_state['target'])
        self.draw_back_button() # Draw back button (positioning is now independent)
        self.draw_bottom_controls(game_state.get('active_scene_name')) # Pass scene name for context
        self.draw_time(game_state['current_t_elapsed_sec'])
        # Draw vectors only if enabled AND simulation has started or finished (velocities exist)
        if self.show_vectors and (game_state['simulation_running'] or game_state['current_t_elapsed_sec'] > 0 or game_state['simulation_paused']):
             self.draw_vectors(game_state)


    def draw_back_button(self):
        """Draws the Back button."""
        pygame.draw.rect(self.screen, cfg.GRAY, self.back_button_rect, border_radius=cfg.BUTTON_BORDER_RADIUS)
        utils.draw_text(cfg.BACK_BUTTON_TEXT, self.font_back_button, cfg.BLACK, self.screen, self.back_button_rect.centerx, self.back_button_rect.centery, center=True)

    def draw_scene_title(self, title):
        """Draws the current scene title at the top."""
        # No longer need to adjust Y position based on back button
        title_y = cfg.SCENE_TITLE_Y
        if title:
             utils.draw_text(title, self.font_title, cfg.WHITE, self.screen, cfg.WIDTH / 2, title_y, center=True)

    def draw_formulas(self, game_state):
        """Draws the formula text display."""
        line_height = self.font_formula.get_linesize() * cfg.FORMULA_LINE_HEIGHT_MULTIPLIER
        col1_x = cfg.FORMULA_COL1_X
        col2_x = cfg.FORMULA_COL2_X

        # Kinematic Equations
        utils.draw_text("Kinematik Denklemler:", self.font_medium, cfg.WHITE, self.screen, col1_x, cfg.FORMULA_Y_START)
        utils.draw_text(f"x(t) = V0x * t", self.font_formula, cfg.WHITE, self.screen, col1_x, cfg.FORMULA_Y_START + line_height * 1.2)
        utils.draw_text(f"y(t) = V0y * t - 0.5 * g * t²", self.font_formula, cfg.WHITE, self.screen, col1_x, cfg.FORMULA_Y_START + line_height * 2.2)
        utils.draw_text(f"(g = {cfg.G_METERS_PER_SEC2} m/s², V0y yukarı pozitif)", self.font_small, cfg.LIGHT_GRAY, self.screen, col1_x, cfg.FORMULA_Y_START + line_height * 3.2)

        # Instantaneous Calculations
        current_displacement_x_m = 0.0
        current_displacement_y_m = 0.0
        proj = game_state.get('projectile')
        # Only calculate if simulation has state (avoids errors on first frame/reset)
        if proj and (game_state.get('simulation_running') or game_state.get('current_t_elapsed_sec') > 0 or game_state.get('simulation_paused')):
            try:
                current_displacement_x_m = utils.px_to_m(proj.current_pos_px[0] - proj.initial_pos_px[0])
                # Physics Y (positive upwards from start)
                current_displacement_y_m = utils.px_to_m(proj.initial_pos_px[1] - proj.current_pos_px[1])
            except (AttributeError, IndexError): pass # Ignore errors if projectile state isn't ready

        utils.draw_text("Anlık Hesaplamalar:", self.font_medium, cfg.WHITE, self.screen, col2_x, cfg.FORMULA_Y_START)
        elapsed_t = game_state.get('current_t_elapsed_sec', 0.0)
        launch_vx_mps = game_state.get('launch_v0x_mps_display', 0.0)
        launch_vy_mps = game_state.get('launch_v0y_mps_display', 0.0)
        x_calc_text = f"ΔX: {current_displacement_x_m:.2f}m = {launch_vx_mps:.2f}m/s * {elapsed_t:.2f}s"
        y_calc_text = f"ΔY: {current_displacement_y_m:.2f}m = {launch_vy_mps:.2f}m/s * {elapsed_t:.2f}s - 0.5*{cfg.G_METERS_PER_SEC2:.2f}*({elapsed_t:.2f}s)²"
        utils.draw_text(x_calc_text, self.font_formula, cfg.WHITE, self.screen, col2_x, cfg.FORMULA_Y_START + line_height * 1.2)
        utils.draw_text(y_calc_text, self.font_formula, cfg.WHITE, self.screen, col2_x, cfg.FORMULA_Y_START + line_height * 2.2)

        # Display Target Time (adjust label based on scene)
        active_scene_name = game_state.get('active_scene_name')
        target_time_label = "Hedef t"
        if active_scene_name == "Yatay Atış":
             target_time_label = "Hesap. t"
        elif active_scene_name == "Dikey Atış":
             target_time_label = "Toplam t"
        t_target_str_disp = f"{target_time_label} = {game_state.get('time_to_target_sec', 0.0):.2f} s"
        utils.draw_text(t_target_str_disp, self.font_formula, cfg.WHITE, self.screen, col2_x, cfg.FORMULA_Y_START + line_height * 3.2)


    def draw_formula_controls(self, simulation_paused, simulation_speed_multiplier):
        """Draws the pause/resume and speed control buttons."""
        pause_text = "Devam Et" if simulation_paused else "Durdur"
        pygame.draw.rect(self.screen, cfg.LIGHT_GRAY, self.pause_button_rect, border_radius=cfg.BUTTON_BORDER_RADIUS)
        utils.draw_text(pause_text, self.font_medium, cfg.BLACK, self.screen, self.pause_button_rect.centerx, self.pause_button_rect.centery, center=True)
        pygame.draw.rect(self.screen, cfg.LIGHT_GRAY, self.speed_minus_button_rect, border_radius=cfg.BUTTON_BORDER_RADIUS)
        utils.draw_text("-", self.font_large, cfg.BLACK, self.screen, self.speed_minus_button_rect.centerx, self.speed_minus_button_rect.centery, center=True)
        pygame.draw.rect(self.screen, cfg.LIGHT_GRAY, self.speed_plus_button_rect, border_radius=cfg.BUTTON_BORDER_RADIUS)
        utils.draw_text("+", self.font_large, cfg.BLACK, self.screen, self.speed_plus_button_rect.centerx, self.speed_plus_button_rect.centery, center=True)
        speed_text = f"Hız: {simulation_speed_multiplier:.1f}x"
        utils.draw_text(speed_text, self.font_medium, cfg.WHITE, self.screen, self.speed_minus_button_rect.right + (self.speed_plus_button_rect.left - self.speed_minus_button_rect.right) // 2, self.speed_minus_button_rect.centery, center=True)

    def draw_separator(self):
        """Draws the line separating formula area from main simulation area."""
        line_y = cfg.FORMULA_AREA_HEIGHT - cfg.FORMULA_AREA_LINE_Y_OFFSET
        pygame.draw.line(self.screen, cfg.WHITE, (0, line_y), (cfg.WIDTH, line_y), cfg.FORMULA_AREA_LINE_THICKNESS)

    def draw_sliders(self, projectile, target):
        """Draws the sliders with handles, labels, and coordinates for ENABLED sliders."""
        slider_labels = {"circle_x": "Çember X0", "circle_y": "Çember Y0", "box_x": "Kutu X", "box_y": "Kutu Y"}
        if not projectile or not target: return

        # Iterate ONLY through the sliders enabled for this scene
        for key in self.sliders_enabled:
            # Safely get track and handle rects (get_slider_handle_rect checks enablement)
            track_rect = self.slider_rects_track.get(key)
            handle_rect = self.get_slider_handle_rect(key)

            # Skip drawing if rects are missing (shouldn't happen for enabled sliders if defined)
            if not track_rect or not handle_rect:
                 # print(f"Warning: Missing rect for enabled slider '{key}'") # Optional debug
                 continue

            # Draw Track and Handle
            pygame.draw.rect(self.screen, cfg.GRAY, track_rect, border_radius=cfg.SLIDER_TRACK_BORDER_RADIUS)
            pygame.draw.rect(self.screen, cfg.BLACK, handle_rect, border_radius=cfg.SLIDER_HANDLE_BORDER_RADIUS)

            # Draw Label
            label_text = slider_labels.get(key, "??")
            label_x = track_rect.left
            label_y = track_rect.bottom + cfg.SLIDER_LABEL_Y_OFFSET
            utils.draw_text(label_text, self.font_small, cfg.WHITE, self.screen, label_x, label_y)
            label_textobj = self.font_small.render(label_text, True, cfg.WHITE)
            label_textrect = label_textobj.get_rect(topleft=(label_x, label_y))

            # Draw Coordinate Text
            coord_text = ""
            coord_m = 0 # Default
            try:
                # Calculate coordinate based on slider key
                if key == "circle_x":
                     coord_m = utils.px_to_m(projectile.initial_pos_px[0])
                     coord_text = f"(X: {coord_m:.1f}m)"
                elif key == "circle_y":
                    # Display Y coordinate relative to ground (Pygame Y=HEIGHT is ground)
                    coord_m = utils.px_to_m(cfg.HEIGHT - projectile.initial_pos_px[1]) # Physics Y relative to ground
                    coord_text = f"(Y: {coord_m:.1f}m)"
                elif key == "box_x":
                     # For box, display center coordinate
                     coord_m = utils.px_to_m(target.center_pos_px[0])
                     coord_text = f"(X Mer.: {coord_m:.1f}m)"
                elif key == "box_y":
                     # Display box center Y coordinate relative to ground
                     coord_m = utils.px_to_m(cfg.HEIGHT - target.center_pos_px[1]) # Physics Y relative to ground
                     coord_text = f"(Y Mer.: {coord_m:.1f}m)"

                # Draw the coordinate text if calculated
                if coord_text:
                    coord_x = label_textrect.right + cfg.SLIDER_LABEL_COORD_SPACING_X
                    coord_y = label_y
                    utils.draw_text(coord_text, self.font_small, cfg.LIGHT_GRAY, self.screen, coord_x, coord_y)
            except (IndexError, AttributeError, TypeError, NameError) as e:
                 # print(f"Error drawing coordinate for slider {key}: {e}") # Optional debug
                 pass # Don't crash if coordinate calculation fails

    def draw_bottom_controls(self, active_scene_name=None):
        """Draws the input box and main action buttons, adjusting for scene context."""
        # Determine Input Box Color
        input_box_color = cfg.INPUT_BOX_ACTIVE_COLOR if self.input_active else cfg.INPUT_BOX_INACTIVE_COLOR
        if self.input_error: input_box_color = cfg.ERROR_COLOR

        # Draw Input Box and Border
        pygame.draw.rect(self.screen, input_box_color, self.input_box_rect, border_radius=cfg.BUTTON_BORDER_RADIUS)
        pygame.draw.rect(self.screen, cfg.BLACK, self.input_box_rect, cfg.INPUT_BOX_BORDER_WIDTH, border_radius=cfg.BUTTON_BORDER_RADIUS)

        # Draw Text Inside Input Box
        utils.draw_text(self.time_to_target_str, self.font_medium, cfg.BLACK, self.screen, self.input_box_rect.x + cfg.INPUT_TEXT_X_OFFSET, self.input_box_rect.y + cfg.INPUT_TEXT_Y_OFFSET)

        # Determine and Draw Input Label Text and Color based on Scene
        input_label_text = "Hedef Süre (s):" # Default
        input_label_color = cfg.WHITE
        if active_scene_name == "Yatay Atış":
            input_label_text = "Hesaplanan Süre:"
            input_label_color = cfg.GRAY # Gray out as it's calculated
        elif active_scene_name == "Dikey Atış":
             input_label_text = "Toplam Süre (s):" # Indicate round trip time
             input_label_color = cfg.WHITE # User inputs this

        utils.draw_text(input_label_text, self.font_small, input_label_color, self.screen, self.input_box_rect.left, self.input_box_rect.top + cfg.INPUT_LABEL_Y_OFFSET)

        # Draw Error Message if present
        if self.error_message:
            error_text_y = self.input_box_rect.top + cfg.INPUT_LABEL_Y_OFFSET - self.font_small.get_height() - 2
            utils.draw_text(self.error_message, self.font_small, cfg.ERROR_COLOR, self.screen, self.input_box_rect.left, error_text_y)

        # Draw Buttons
        pygame.draw.rect(self.screen, cfg.LIGHT_GRAY, self.launch_button_rect, border_radius=cfg.BUTTON_BORDER_RADIUS)
        utils.draw_text("Fırlat", self.font_medium, cfg.BLACK, self.screen, self.launch_button_rect.centerx, self.launch_button_rect.centery, center=True)

        pygame.draw.rect(self.screen, cfg.LIGHT_GRAY, self.restart_button_rect, border_radius=cfg.BUTTON_BORDER_RADIUS)
        utils.draw_text("Yeniden Başlat", self.font_medium, cfg.BLACK, self.screen, self.restart_button_rect.centerx, self.restart_button_rect.centery, center=True)

        pygame.draw.rect(self.screen, cfg.LIGHT_GRAY, self.toggle_vec_vis_button_rect, border_radius=cfg.BUTTON_BORDER_RADIUS)
        vec_vis_text = "Vektör Gizle" if self.show_vectors else "Vektör Göster"
        utils.draw_text(vec_vis_text, self.font_medium, cfg.BLACK, self.screen, self.toggle_vec_vis_button_rect.centerx, self.toggle_vec_vis_button_rect.centery, center=True)

        pygame.draw.rect(self.screen, cfg.LIGHT_GRAY, self.toggle_vec_mode_button_rect, border_radius=cfg.BUTTON_BORDER_RADIUS)
        vec_mode_text = "Bileşen Göster" if self.show_velocity_vector else "Toplam Hız Göster"
        utils.draw_text(vec_mode_text, self.font_medium, cfg.BLACK, self.screen, self.toggle_vec_mode_button_rect.centerx, self.toggle_vec_mode_button_rect.centery, center=True)

        pygame.draw.rect(self.screen, cfg.LIGHT_GRAY, self.toggle_vec_type_button_rect, border_radius=cfg.BUTTON_BORDER_RADIUS)
        vec_type_text = "Hız Vek. Göster" if self.show_acceleration_vector else "İvme Vek. Göster"
        utils.draw_text(vec_type_text, self.font_medium, cfg.BLACK, self.screen, self.toggle_vec_type_button_rect.centerx, self.toggle_vec_type_button_rect.centery, center=True)


    def draw_vectors(self, game_state):
        """Draws velocity and/or acceleration vectors."""
        proj = game_state.get('projectile')
        if not proj: return
        vx = game_state.get('current_vx_px_s', 0.0)
        vy = game_state.get('current_vy_px_s', 0.0)
        center_x = int(proj.current_pos_px[0])
        center_y = int(proj.current_pos_px[1])
        vx_mps = utils.px_s_to_mps(vx)
        vy_mps = utils.px_s_to_mps(-vy) # Physics coords (up positive)

        # Draw Acceleration Vector (always down)
        if self.show_acceleration_vector:
            accel_y_px = cfg.GRAVITY_PX_PER_SEC2 # Positive (down in pygame)
            end_x = center_x
            # Scale the visual length for better visibility
            end_y = center_y + accel_y_px * cfg.VECTOR_SCALE * cfg.ACCELERATION_VECTOR_SCALE_MULTIPLIER
            utils.draw_arrow(self.screen, cfg.GREEN, (center_x, center_y), (end_x, end_y), cfg.VECTOR_ARROW_SIZE)
            utils.draw_text(f"a: {cfg.G_METERS_PER_SEC2:.2f} m/s²", self.font_small, cfg.GREEN, self.screen, end_x + cfg.VECTOR_TEXT_OFFSET_X, end_y + cfg.VECTOR_TEXT_OFFSET_Y_DOWN)
        # Draw Velocity Vector(s)
        else:
            # Only draw if there's significant velocity
            if abs(vx) > 1e-6 or abs(vy) > 1e-6:
                # Combined Velocity Vector
                if self.show_velocity_vector:
                    mag_px_s = math.hypot(vx, vy)
                    end_x = center_x + vx * cfg.VECTOR_SCALE
                    end_y = center_y + vy * cfg.VECTOR_SCALE
                    utils.draw_arrow(self.screen, cfg.MAGENTA, (center_x, center_y), (end_x, end_y), cfg.VECTOR_ARROW_SIZE)
                    mag_mps = utils.px_s_to_mps(mag_px_s)
                    # Adjust text position based on vector direction
                    text_x = end_x + cfg.VECTOR_COMBINED_OFFSET * math.copysign(1, vx) if vx != 0 else end_x + cfg.VECTOR_COMBINED_OFFSET
                    text_y = end_y + (cfg.VECTOR_COMBINED_OFFSET * math.copysign(1, vy) if vy != 0 else cfg.VECTOR_COMBINED_OFFSET)
                    utils.draw_text(f"Hız: {mag_mps:.2f} m/s", self.font_small, cfg.MAGENTA, self.screen, text_x, text_y)
                # Velocity Components (Vx and Vy)
                else:
                    # Draw Vx only if non-zero
                    if abs(vx) > 1e-6:
                        end_x_vx = center_x + vx * cfg.VECTOR_SCALE
                        end_y_vx = center_y
                        utils.draw_arrow(self.screen, cfg.WHITE, (center_x, center_y), (end_x_vx, end_y_vx), cfg.VECTOR_ARROW_SIZE)
                        utils.draw_text(f"Vx: {vx_mps:.2f} m/s", self.font_small, cfg.WHITE, self.screen, end_x_vx + cfg.VECTOR_TEXT_OFFSET_X, end_y_vx + cfg.VECTOR_TEXT_OFFSET_Y_UP)
                    # Draw Vy only if non-zero
                    if abs(vy) > 1e-6:
                        end_x_vy = center_x
                        end_y_vy = center_y + vy * cfg.VECTOR_SCALE
                        utils.draw_arrow(self.screen, cfg.BLACK, (center_x, center_y), (end_x_vy, end_y_vy), cfg.VECTOR_ARROW_SIZE)
                        # Adjust label y position based on vector direction (up/down)
                        label_y = end_y_vy + cfg.VECTOR_TEXT_OFFSET_Y_DOWN if vy >= 0 else end_y_vy + cfg.VECTOR_TEXT_OFFSET_Y_UP
                        utils.draw_text(f"Vy: {vy_mps:.2f} m/s", self.font_small, cfg.BLACK, self.screen, end_x_vy + cfg.VECTOR_TEXT_OFFSET_X, label_y)

    def draw_time(self, elapsed_time_sec):
        """Draws the elapsed simulation time."""
        time_text_x = cfg.TIME_TEXT_X_OFFSET
        # Position time text relative to bottom controls
        time_text_y = cfg.CONTROL_AREA_Y_START - cfg.TIME_TEXT_Y_OFFSET # Place above controls
        utils.draw_text(f"Geçen Süre: {elapsed_time_sec:.2f} s", self.font_small, cfg.WHITE, self.screen, time_text_x, time_text_y)