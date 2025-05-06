# main.py
# -*- coding: utf-8 -*- # Türkçe karakterler için
import pygame
import sys
import math
import pygame.font # Font kullanımı için eklendi
# Import configurations
import config as cfg
# Import utility functions
import utils
# Import game object classes
from game_objects import Projectile, Target
# Import physics engine
from physics import PhysicsEngine
# Import UI manager
from ui import UIManager

# --- Game States ---
SELECTION = 0
SIMULATION = 1

# --- Pygame Setup (Global) ---
pygame.init()
screen = pygame.display.set_mode((cfg.WIDTH, cfg.HEIGHT))
pygame.display.set_caption("Atış Simülasyonu - Sahne Seçin") # Initial caption
clock = pygame.time.Clock()
# Define fonts needed globally or in functions
try:
    font_medium = pygame.font.Font(None, cfg.FONT_SIZE_MEDIUM)
    font_small = pygame.font.Font(None, cfg.FONT_SIZE_SMALL)
    font_large = pygame.font.Font(None, cfg.FONT_SIZE_LARGE) # For selection title
except Exception as e:
    print(f"Error loading fonts: {e}")
    pygame.quit()
    sys.exit()


# --- Global Simulation Variables (Initialized when scene is selected) ---
active_scene_name = None
active_scene_config = None
projectile = None
target = None
physics_engine = None
ui_manager = None

# Game state variables (initialized/reset in reset_simulation)
launch_v0x_px_s = 0.0
launch_v0y_px_s = 0.0
current_vx_px_s = 0.0
current_vy_px_s = 0.0
simulation_running = False
simulation_paused = False
simulation_start_time_sec = 0.0
time_paused_offset_sec = 0.0
simulation_speed_multiplier = 1.0
time_to_target_sec = 2.0 # Default, will be overwritten
launch_v0x_mps_display = 0.0
launch_v0y_mps_display = 0.0
current_t_elapsed_sec = 0.0
pause_start_time_sec = 0.0 # Track when pause began
projectile_trail = [] # Mermi iz noktalarını saklamak için liste
time_last_trail_point_sec = 0.0 # Son iz noktasının eklendiği zaman (efektif simülasyon zamanı)
# --- Peak Info Variables ---
peak_time_sec = 0.0          # Tepe noktasına ulaşma süresi
peak_position_px = None    # Tepe noktasının [x, y] konumu (piksel)
show_peak_info = False     # Tepe noktası bilgisini gösterme bayrağı

# --- Helper Functions ---

def draw_button(surface, text, rect, button_color, text_color, font, border_radius=cfg.BUTTON_BORDER_RADIUS):
    """Draws a button with text."""
    pygame.draw.rect(surface, button_color, rect, border_radius=border_radius)
    text_surf = font.render(text, True, text_color)
    text_rect = text_surf.get_rect(center=rect.center)
    surface.blit(text_surf, text_rect)

def draw_selection_screen(surface):
    """Draws the scene selection screen and returns button rects."""
    surface.fill(cfg.BLACK) # Background
    button_rects = {}
    button_width = cfg.BUTTON_WIDTH * 1.5 # Make buttons wider for scene names
    button_height = cfg.BUTTON_HEIGHT * 1.2
    start_y = cfg.HEIGHT // 2 - (len(cfg.SCENES) * (button_height + cfg.SPACING_PX)) // 2
    button_x = (cfg.WIDTH - button_width) // 2

    # Draw Title
    title_surf = font_large.render("Sahne Seçin", True, cfg.WHITE)
    title_rect = title_surf.get_rect(center=(cfg.WIDTH // 2, start_y - button_height))
    surface.blit(title_surf, title_rect)

    # Draw Buttons
    current_y = start_y
    for scene_name in cfg.SCENES.keys():
        rect = pygame.Rect(button_x, current_y, button_width, button_height)
        draw_button(surface, scene_name, rect, cfg.BLUE, cfg.WHITE, font_medium)
        button_rects[scene_name] = rect
        current_y += button_height + cfg.SPACING_PX

    pygame.display.flip()
    return button_rects

def initialize_simulation(scene_name):
    """Initializes all components for the selected simulation scene."""
    global active_scene_name, active_scene_config, projectile, target
    global physics_engine, ui_manager, time_to_target_sec
    global projectile_trail, time_last_trail_point_sec # Trail variables reset here too
    global peak_time_sec, peak_position_px, show_peak_info # Peak info variables reset here too

    active_scene_name = scene_name
    try:
        active_scene_config = cfg.SCENES[active_scene_name]
    except KeyError:
        print(f"Error: Scene '{scene_name}' not found in config.py. Returning to selection.")
        return False # Indicate failure

    # --- Initialize Simulation Components ---
    pygame.display.set_caption(active_scene_config.get("title", "Atış Simülasyonu"))
    projectile = Projectile(initial_pos_px=list(active_scene_config["initial_projectile_pos"])) # Use list copy
    target = Target(initial_pos_px=list(active_scene_config["initial_target_pos"])) # Use list copy
    physics_engine = PhysicsEngine()
    ui_manager = UIManager(screen, active_scene_config) # Pass scene config to UI

    # --- Specific Initialization for Dikey Atış ---
    if active_scene_name == "Dikey Atış":
        # Set target's position to match the projectile's initial position
        target.set_position(list(projectile.initial_pos_px)) # Use list copy
        # Adjust target position visually to its center (as it's not drawn)
        target.set_position([projectile.initial_pos_px[0] - target.width / 2,
                             projectile.initial_pos_px[1] - target.height / 2])


    ui_manager.initialize_sliders(projectile, target) # Initialize sliders based on scene config

    # --- Reset State Variables ---
    # Set default time from config BEFORE resetting, so reset uses the correct value
    time_to_target_sec = float(active_scene_config.get("default_time_str", "2.0"))
    reset_simulation() # Reset all simulation variables and UI state

    # Clear trail and peak info for the new scene explicitly (reset_simulation also does this)
    projectile_trail.clear()
    time_last_trail_point_sec = 0.0
    peak_time_sec = 0.0
    peak_position_px = None
    show_peak_info = False

    return True # Indicate success

# --- Simulation Helper Functions (Need access to global simulation variables) ---

def update_positions_from_sliders():
    """Updates initial projectile and target positions based on active sliders."""
    # Ensure components are initialized
    if not ui_manager or not projectile or not target or not active_scene_config:
        return

    sliders = ui_manager.sliders
    sliders_enabled = active_scene_config.get("sliders_enabled", []) # Get enabled sliders for scene

    drawable_height = cfg.DRAWABLE_HEIGHT
    y_offset = cfg.DRAWABLE_Y_OFFSET

    # Calculate current positions BEFORE calculating ranges
    current_proj_x = projectile.initial_pos_px[0]
    current_proj_y = projectile.initial_pos_px[1]
    current_target_x = target.pos_px[0]
    current_target_y = target.pos_px[1]

    # Calculate Ranges
    circle_range_x = cfg.WIDTH - 2 * projectile.radius
    circle_range_y = drawable_height - 2 * projectile.radius
    box_range_x = cfg.WIDTH - target.width
    box_range_y = drawable_height - target.height

    # Update Positions based on ENABLED sliders
    new_proj_x = current_proj_x
    new_proj_y = current_proj_y
    new_target_x = current_target_x
    new_target_y = current_target_y

    if "circle_x" in sliders_enabled and "circle_x" in sliders:
        # Check range to avoid division by zero if width is too small
        new_proj_x = projectile.radius + sliders.get("circle_x", 0.5) * circle_range_x if circle_range_x > 0 else projectile.radius
    if "circle_y" in sliders_enabled and "circle_y" in sliders:
        # Check range to avoid division by zero
        new_proj_y = y_offset + projectile.radius + sliders.get("circle_y", 0.5) * circle_range_y if circle_range_y > 0 else y_offset + projectile.radius
    if "box_x" in sliders_enabled and "box_x" in sliders:
        new_target_x = sliders.get("box_x", 0.5) * box_range_x if box_range_x > 0 else 0
    if "box_y" in sliders_enabled and "box_y" in sliders:
        new_target_y = y_offset + sliders.get("box_y", 0.5) * box_range_y if box_range_y > 0 else y_offset # Box Y maps like circle Y


    # Apply updates
    projectile.set_initial_position([new_proj_x, new_proj_y])

    # --- Special handling for Dikey Atış target position ---
    if active_scene_name == "Dikey Atış":
        # Target always mirrors projectile's initial position (centered)
        target.set_position([new_proj_x - target.width / 2, new_proj_y - target.height / 2])
    else:
        target.set_position([new_target_x, new_target_y])


    # If sim not running, ensure current projectile pos is reset
    if not simulation_running:
        projectile.reset_to_initial()

def reset_simulation():
    """Resets the simulation state and UI elements for the current scene."""
    global simulation_running, launch_v0x_px_s, launch_v0y_px_s, current_vx_px_s, current_vy_px_s
    global launch_v0x_mps_display, launch_v0y_mps_display, current_t_elapsed_sec
    global simulation_paused, time_paused_offset_sec, time_to_target_sec
    global projectile_trail, time_last_trail_point_sec
    global peak_time_sec, peak_position_px, show_peak_info # <--- TEPE NOKTASI DEĞİŞKENLERİNİ EKLE

    # Ensure components are initialized
    if not ui_manager or not projectile or not target or not active_scene_config:
        print("Warning: reset_simulation called before initialization.")
        return

    # Reset simulation state
    simulation_running = False
    simulation_paused = False
    time_paused_offset_sec = 0.0
    launch_v0x_px_s = 0.0
    launch_v0y_px_s = 0.0
    current_vx_px_s = 0.0
    current_vy_px_s = 0.0
    launch_v0x_mps_display = 0.0
    launch_v0y_mps_display = 0.0
    current_t_elapsed_sec = 0.0

    # Reset UI input/state using the active scene's default time
    default_time_str = active_scene_config.get("default_time_str", "2.0")
    ui_manager.time_to_target_str = default_time_str
    ui_manager.input_error = False
    ui_manager.error_message = None # Clear error message on reset
    try:
        time_to_target_sec = float(default_time_str) # Reset validated time
    except ValueError:
        time_to_target_sec = 2.0 # Fallback default
        ui_manager.time_to_target_str = "2.0"


    # Reset vector display toggles in UI Manager to defaults
    ui_manager.show_vectors = True
    ui_manager.show_velocity_vector = False
    ui_manager.show_acceleration_vector = False

    # Reset object positions based on sliders (or initial scene config if sliders absent)
    # Need to re-initialize sliders if they weren't before calling reset
    if ui_manager: # Only if ui_manager exists
        ui_manager.initialize_sliders(projectile, target)
    update_positions_from_sliders() # This will set initial positions based on sliders/defaults
    if projectile: # Only if projectile exists
        projectile.reset_to_initial() # Ensure projectile is at its *initial* pos

    # Clear the projectile trail
    projectile_trail.clear() # <--- İZİ TEMİZLE
    time_last_trail_point_sec = 0.0 # <--- ZAMANLAYICIYI SIFIRLA

    # Reset peak info
    peak_time_sec = 0.0         # <--- TEPE SÜRESİNİ SIFIRLA
    peak_position_px = None   # <--- TEPE KONUMUNU SIFIRLA
    show_peak_info = False    # <--- GÖSTERME BAYRAĞINI SIFIRLA

# --- Main Loop ---
running = True
game_state = SELECTION # Start in selection mode
selection_buttons = {} # To store button rects

while running:
    current_time_sec_abs = pygame.time.get_ticks() / 1000.0

    # --- State Machine ---
    if game_state == SELECTION:
        # --- Selection Screen Logic ---
        if not selection_buttons: # Draw only once unless needed again
             selection_buttons = draw_selection_screen(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False; break
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # Left click
                    mouse_pos = event.pos
                    for scene_name, rect in selection_buttons.items():
                        if rect.collidepoint(mouse_pos):
                            print(f"Selected scene: {scene_name}")
                            if initialize_simulation(scene_name):
                                game_state = SIMULATION
                                selection_buttons = {} # Clear buttons for next time
                            else:
                                # Handle initialization error (e.g., stay in selection)
                                print("Failed to initialize simulation. Staying in selection.")
                                selection_buttons = {} # Redraw selection screen
                            break # Stop checking buttons once one is clicked
        if not running: break

    elif game_state == SIMULATION:
        # --- Simulation Logic ---

        # Ensure components are loaded (safety check)
        if not ui_manager or not projectile or not target or not physics_engine or not active_scene_config:
             print("Error: Simulation components not initialized. Returning to selection.")
             game_state = SELECTION
             selection_buttons = {}
             pygame.display.set_caption("Atış Simülasyonu - Sahne Seçin")
             projectile_trail.clear() # Clear trail when returning to menu due to error
             time_last_trail_point_sec = 0.0
             peak_time_sec = 0.0         # Clear peak info on error return
             peak_position_px = None
             show_peak_info = False
             continue # Skip rest of the loop iteration

        # --- Event Handling (Simulation) ---
        action_from_ui = None
        back_to_menu_requested = False # Flag for returning to menu

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False; break

            # Check for ESC key press to go back
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    back_to_menu_requested = True
                    break # Exit event loop immediately

            # Let UI Manager handle its events (buttons, sliders, input)
            action_from_ui = ui_manager.handle_event(event, simulation_running, simulation_paused)

            # Check if the UI manager itself triggered the back action
            if action_from_ui == "back_to_menu":
                back_to_menu_requested = True
                break # Exit event loop immediately

            # If UI handled an event, we might not need to process further in this loop
            # (Depends on the specific action)
            if action_from_ui and action_from_ui != "update_slider": # Allow slider updates to fall through
                 pass # Continue processing other events or simulation logic

        if not running: break

        # Handle request to return to menu (from ESC or Back button)
        if back_to_menu_requested:
            game_state = SELECTION
            selection_buttons = {} # Force redraw of selection screen
            pygame.display.set_caption("Atış Simülasyonu - Sahne Seçin")
            # Reset simulation variables to None to release resources (optional but good practice)
            projectile = None
            target = None
            physics_engine = None
            ui_manager = None
            active_scene_name = None
            active_scene_config = None
            projectile_trail.clear() # <--- MENÜYE DÖNERKEN İZİ TEMİZLE
            time_last_trail_point_sec = 0.0 # <--- ZAMANLAYICIYI SIFIRLA
            # Reset peak info when returning to menu
            peak_time_sec = 0.0         # <--- TEPE SÜRESİNİ SIFIRLA
            peak_position_px = None   # <--- TEPE KONUMUNU SIFIRLA
            show_peak_info = False    # <--- GÖSTERME BAYRAĞINI SIFIRLA
            continue # Skip the rest of the simulation logic for this frame

        # --- Process Actions from UI (Simulation) ---
        if action_from_ui == "launch":
            projectile_trail.clear() # <--- FIRLATMADAN ÖNCE ESKİ İZİ TEMİZLE
            time_last_trail_point_sec = 0.0 # <--- ZAMANLAYICIYI SIFIRLA
            show_peak_info = False # Yeni fırlatmada tepe bilgisi gösterilmez
            peak_time_sec = 0.0    # Reset peak values before calculation
            peak_position_px = None
            ui_manager.error_message = None # Clear previous errors

            # --- Vertical Launch ("Dikey Atış") Specific Logic ---
            if active_scene_name == "Dikey Atış":
                valid_time = ui_manager.validate_time_input()
                if valid_time is not None:
                    time_to_target_sec = valid_time # This is total round-trip time
                    simulation_running = False # Ensure reset
                    simulation_paused = False
                    time_paused_offset_sec = 0.0
                    current_t_elapsed_sec = 0.0
                    update_positions_from_sliders() # Ensure start pos is current
                    projectile.reset_to_initial()
                    ui_manager.show_vectors = True
                    ui_manager.show_velocity_vector = False
                    ui_manager.show_acceleration_vector = False

                    # Calculate V0y needed to return in time_to_target_sec
                    t_peak = time_to_target_sec / 2.0
                    gravity_px_s2 = physics_engine.gravity_px_s2
                    v0y_physics_px_s = gravity_px_s2 * t_peak
                    launch_v0y_px_s = -v0y_physics_px_s
                    launch_v0x_px_s = 0.0 # No horizontal velocity

                    launch_v0x_mps_display = 0.0
                    launch_v0y_mps_display = utils.px_s_to_mps(-launch_v0y_px_s)

                    simulation_running = True
                    simulation_start_time_sec = current_time_sec_abs
                    current_vx_px_s = launch_v0x_px_s
                    current_vy_px_s = launch_v0y_px_s

                    # --- Calculate and Store Peak Info (Dikey Atış) ---
                    if physics_engine.gravity_px_s2 > 0:
                        v0y_physics = -launch_v0y_px_s # Physics coords (up positive)
                        if v0y_physics > 1e-6: # Only if launched upwards (check against small threshold)
                            peak_time_sec = v0y_physics / physics_engine.gravity_px_s2
                            peak_position_px, _ = physics_engine.calculate_kinematic_update(
                                projectile.initial_pos_px, launch_v0x_px_s, launch_v0y_px_s, peak_time_sec
                            )
                        else: # Launched downwards or V0y=0
                            peak_time_sec = 0.0
                            peak_position_px = list(projectile.initial_pos_px)
                    # --- End Peak Info Calculation ---


            # --- Horizontal Launch ("Yatay Atış") Specific Logic ---
            elif active_scene_name == "Yatay Atış":
                update_positions_from_sliders() # Ensure positions are based on current slider values
                initial_y_proj = projectile.initial_pos_px[1]
                target_y_for_calc = target.center_pos_px[1]

                if initial_y_proj >= target_y_for_calc:
                    ui_manager.input_error = True
                    ui_manager.error_message = "Yatay atış mümkün değil! (Hedef merkezi başlangıcın altında olmalı)"
                    time_to_target_sec = 0
                else:
                    ui_manager.input_error = False
                    ui_manager.error_message = None
                    delta_y_physics_px = target_y_for_calc - initial_y_proj
                    gravity_px_s2 = physics_engine.gravity_px_s2

                    if gravity_px_s2 > 0 and delta_y_physics_px > 0:
                        try:
                            time_to_target_sec = math.sqrt(2 * delta_y_physics_px / gravity_px_s2)
                        except ValueError:
                            time_to_target_sec = 0
                    else:
                        time_to_target_sec = 0

                    ui_manager.time_to_target_str = f"{time_to_target_sec:.2f}"

                    delta_x_px = target.center_pos_px[0] - projectile.initial_pos_px[0]
                    if time_to_target_sec > 1e-6:
                        launch_v0x_px_s = delta_x_px / time_to_target_sec
                    else:
                        launch_v0x_px_s = 0

                    launch_v0y_px_s = 0.0
                    launch_v0x_mps_display = utils.px_s_to_mps(launch_v0x_px_s)
                    launch_v0y_mps_display = 0.0

                    if time_to_target_sec > 1e-6:
                        simulation_running = False
                        simulation_paused = False
                        time_paused_offset_sec = 0.0
                        current_t_elapsed_sec = 0.0
                        projectile.reset_to_initial()
                        ui_manager.show_vectors = True
                        ui_manager.show_velocity_vector = False
                        ui_manager.show_acceleration_vector = False
                        simulation_running = True
                        simulation_start_time_sec = current_time_sec_abs
                        current_vx_px_s = launch_v0x_px_s
                        current_vy_px_s = launch_v0y_px_s
                    else:
                        simulation_running = False
                        simulation_paused = False
                        current_t_elapsed_sec = 0.0
                        current_vx_px_s = launch_v0x_px_s
                        current_vy_px_s = launch_v0y_px_s

                # Yatay atışta tepe noktası başlangıç noktasıdır, bilgi göstermeyeceğiz
                peak_time_sec = 0.0
                peak_position_px = list(projectile.initial_pos_px) if projectile else None
                show_peak_info = False # Yatay atışta gösterme


            # --- Default Launch Logic (Other Scenes like Eğik Atış) ---
            else: # Eğik Atış ve diğerleri
                valid_time = ui_manager.validate_time_input()
                if valid_time is not None:
                    time_to_target_sec = valid_time
                    simulation_running = False # Ensure reset
                    simulation_paused = False
                    time_paused_offset_sec = 0.0
                    current_t_elapsed_sec = 0.0
                    update_positions_from_sliders()
                    projectile.reset_to_initial()
                    ui_manager.show_vectors = True # Reset vector views
                    ui_manager.show_velocity_vector = False
                    ui_manager.show_acceleration_vector = False

                    launch_v0x_px_s, launch_v0y_px_s = physics_engine.calculate_required_velocities(
                        projectile.initial_pos_px, target.center_pos_px, time_to_target_sec
                    )
                    launch_v0x_mps_display = utils.px_s_to_mps(launch_v0x_px_s)
                    launch_v0y_mps_display = utils.px_s_to_mps(-launch_v0y_px_s) # Y is inverted for display

                    simulation_running = True
                    simulation_start_time_sec = current_time_sec_abs
                    current_vx_px_s = launch_v0x_px_s
                    current_vy_px_s = launch_v0y_px_s

                    # --- Calculate and Store Peak Info (Eğik Atış) ---
                    if physics_engine.gravity_px_s2 > 0:
                        v0y_physics = -launch_v0y_px_s # Physics coords (up positive)
                        if v0y_physics > 1e-6: # Only if launched upwards effectively (check threshold)
                            peak_time_sec = v0y_physics / physics_engine.gravity_px_s2
                            peak_position_px, _ = physics_engine.calculate_kinematic_update(
                                projectile.initial_pos_px, launch_v0x_px_s, launch_v0y_px_s, peak_time_sec
                            )
                        else: # Launched downwards or horizontally (V0y <= 0)
                             peak_time_sec = 0.0
                             peak_position_px = list(projectile.initial_pos_px)
                    # --- End Peak Info Calculation ---


        elif action_from_ui == "reset":
            reset_simulation() # Resets state and positions for the *current* scene
        elif action_from_ui == "pause_toggle":
            simulation_paused = not simulation_paused
            if simulation_paused:
                 pause_start_time_sec = current_time_sec_abs
            else: # Resuming
                time_paused_duration = current_time_sec_abs - pause_start_time_sec
                time_paused_offset_sec += time_paused_duration
        elif action_from_ui == "speed_down":
            simulation_speed_multiplier = max(0.1, round(simulation_speed_multiplier - 0.1, 1))
        elif action_from_ui == "speed_up":
            simulation_speed_multiplier = min(5.0, round(simulation_speed_multiplier + 0.1, 1))
        elif action_from_ui == "update_slider":
             if not simulation_running:
                 update_positions_from_sliders()
        elif action_from_ui == "validate_time":
            if active_scene_name != "Yatay Atış" and active_scene_name != "Dikey Atış":
                valid_time = ui_manager.validate_time_input()
                if valid_time is not None: time_to_target_sec = valid_time

        # --- Simulation Update (Physics Calculation) ---
        effective_t_for_physics = 0.0 # Initialize effective time
        if simulation_running or current_t_elapsed_sec > 0:
            if simulation_paused:
                effective_t_for_physics = current_t_elapsed_sec * simulation_speed_multiplier
            elif not simulation_running and current_t_elapsed_sec > 0 :
                effective_t_for_physics = current_t_elapsed_sec * simulation_speed_multiplier
            else: # Running and not paused
                 t_elapsed_actual = (current_time_sec_abs - simulation_start_time_sec) - time_paused_offset_sec
                 effective_t_for_physics = t_elapsed_actual * simulation_speed_multiplier
                 current_t_elapsed_sec = t_elapsed_actual

            _, current_v_px_s = physics_engine.calculate_kinematic_update(
                 projectile.initial_pos_px, launch_v0x_px_s, launch_v0y_px_s, effective_t_for_physics)
            current_vx_px_s, current_vy_px_s = current_v_px_s
        else: # Before first launch or after reset
             current_vx_px_s, current_vy_px_s = 0.0, 0.0


        # --- Update Projectile Position ---
        if simulation_running and not simulation_paused:
            t_elapsed_effective = effective_t_for_physics # Use already calculated effective time

            if time_to_target_sec > 0 and t_elapsed_effective >= time_to_target_sec:
                # Target Time Reached
                t_final_effective = time_to_target_sec
                current_t_elapsed_sec = time_to_target_sec / simulation_speed_multiplier if simulation_speed_multiplier > 0 else 0

                if active_scene_name == "Dikey Atış":
                    new_projectile_pos, _ = physics_engine.calculate_kinematic_update(
                        projectile.initial_pos_px, launch_v0x_px_s, launch_v0y_px_s, t_final_effective)
                    new_projectile_pos = [new_projectile_pos[0], projectile.initial_pos_px[1]]
                else:
                     new_projectile_pos, _ = physics_engine.calculate_kinematic_update(
                         projectile.initial_pos_px, launch_v0x_px_s, launch_v0y_px_s, t_final_effective)

                projectile.update_position(list(new_projectile_pos))
                simulation_running = False # Stop the simulation state

                # --- Set flag to show peak info AFTER simulation ends (if applicable scene) ---
                if active_scene_name == "Eğik Atış" or active_scene_name == "Dikey Atış":
                    if cfg.PEAK_DOT_ENABLED and peak_position_px is not None: # Check if enabled and calculated
                        show_peak_info = True # Sadece sim bittiğinde göster

                # --- Add final point to trail if enabled ---
                if cfg.TRAIL_ENABLED and projectile:
                    if not projectile_trail or (projectile_trail and projectile_trail[-1] != projectile.current_pos_px):
                        projectile_trail.append(list(projectile.current_pos_px))
                        if len(projectile_trail) > cfg.MAX_TRAIL_POINTS:
                            projectile_trail.pop(0)

            else:
                # Simulation In Progress
                new_projectile_pos, _ = physics_engine.calculate_kinematic_update(
                    projectile.initial_pos_px, launch_v0x_px_s, launch_v0y_px_s, t_elapsed_effective)
                projectile.update_position(new_projectile_pos)

                # --- Add point to trail if enabled and interval passed ---
                if cfg.TRAIL_ENABLED and projectile:
                    if t_elapsed_effective >= time_last_trail_point_sec + cfg.TRAIL_POINT_INTERVAL_SEC:
                        projectile_trail.append(list(projectile.current_pos_px))
                        time_last_trail_point_sec = t_elapsed_effective
                        if len(projectile_trail) > cfg.MAX_TRAIL_POINTS:
                            projectile_trail.pop(0)


        # --- Prepare Game State for UI ---
        display_t_elapsed = 0.0
        if time_to_target_sec > 0 and simulation_speed_multiplier > 0:
             display_t_elapsed = min(current_t_elapsed_sec, time_to_target_sec / simulation_speed_multiplier)
        elif current_t_elapsed_sec > 0:
             display_t_elapsed = current_t_elapsed_sec


        game_state_for_ui = {
            'projectile': projectile, 'target': target,
            'simulation_running': simulation_running, 'simulation_paused': simulation_paused,
            'simulation_speed_multiplier': simulation_speed_multiplier,
            'time_to_target_sec': time_to_target_sec,
            'current_t_elapsed_sec': display_t_elapsed,
            'launch_v0x_px_s': launch_v0x_px_s, 'launch_v0y_px_s': launch_v0y_px_s,
            'launch_v0x_mps_display': launch_v0x_mps_display, 'launch_v0y_mps_display': launch_v0y_mps_display,
            'current_vx_px_s': current_vx_px_s, 'current_vy_px_s': current_vy_px_s,
            'scene_title': active_scene_config.get("title", ""),
            'active_scene_name': active_scene_name
        }

        # --- Drawing (Simulation) ---
        ui_manager.draw_all(game_state_for_ui) # Draw UI elements (including background, buttons, text)

        # --- Draw Projectile Trail ---
        if cfg.TRAIL_ENABLED:
            for point_pos in projectile_trail:
                try:
                    pygame.draw.circle(screen, cfg.TRAIL_POINT_COLOR, (int(point_pos[0]), int(point_pos[1])), cfg.TRAIL_POINT_RADIUS)
                except (IndexError, ValueError, TypeError):
                    pass


        # --- Draw Peak Height Info (if enabled, finished, and applicable scene) ---
        if show_peak_info and peak_position_px and projectile: # Check flag and if data exists
            try:
                # Draw the dot at peak position
                peak_x_draw = int(peak_position_px[0])
                peak_y_draw = int(peak_position_px[1])
                pygame.draw.circle(screen, cfg.PEAK_DOT_COLOR, (peak_x_draw, peak_y_draw), cfg.PEAK_DOT_RADIUS)

                # Calculate peak height relative to start in meters
                peak_height_rel_px = projectile.initial_pos_px[1] - peak_position_px[1] # Pygame Y (down positive)
                peak_height_rel_m = utils.px_to_m(peak_height_rel_px)

                # Prepare text
                peak_text = f"Maks Y: {peak_height_rel_m:.2f}m ({peak_time_sec:.2f}s)"

                # Draw text near the dot
                text_x = peak_x_draw + cfg.PEAK_TEXT_OFFSET_X
                text_y = peak_y_draw + cfg.PEAK_TEXT_OFFSET_Y
                # Ensure font_small is loaded before using it here
                if font_small:
                    utils.draw_text(peak_text, font_small, cfg.PEAK_TEXT_COLOR, screen, text_x, text_y)
                else:
                    print("Error: font_small not loaded, cannot draw peak text.")


            except (TypeError, IndexError, AttributeError, ValueError) as e: # Added ValueError
                print(f"Error drawing peak info: {e}") # Hata ayıklama için
                show_peak_info = False # Hata olursa tekrar çizmeye çalışma


        # Draw target only if it's NOT the "Dikey Atış" scene
        if active_scene_name != "Dikey Atış":
            target.draw(screen)                   # Draw target

        if projectile: # Ensure projectile exists before drawing
            projectile.draw(screen)               # Draw projectile (on top of trail and peak dot)

        pygame.display.flip()

    # --- Common ---
    clock.tick(60)

# --- Cleanup ---
pygame.quit()
sys.exit()