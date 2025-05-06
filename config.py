# config.py
import pygame

# --- Scaling Factors ---
SCALE_FACTOR = 0.75
SECONDARY_SCALE = 1.5 # Scale up fonts and UI elements slightly

# --- Original Dimensions (for reference during scaling) ---
ORIG_WIDTH, ORIG_HEIGHT = 1850, 950

# --- Scaled Constants ---
WIDTH = int(ORIG_WIDTH * SCALE_FACTOR)
HEIGHT = int(ORIG_HEIGHT * SCALE_FACTOR)

# --- Colors ---
BLUE = (0, 100, 200)
YELLOW = (255, 255, 0)
RED = (200, 0, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (150, 150, 150)
LIGHT_GRAY = (200, 200, 200)
MAGENTA = (255, 0, 255)
GREEN = (0, 200, 0)
INPUT_BOX_ACTIVE_COLOR = WHITE
INPUT_BOX_INACTIVE_COLOR = LIGHT_GRAY
ERROR_COLOR = (255, 100, 100)

# Apply secondary scaling to sizes
CIRCLE_RADIUS_PX = int(15 * SCALE_FACTOR * SECONDARY_SCALE)
BOX_WIDTH_PX = int(50 * SCALE_FACTOR * SECONDARY_SCALE)
BOX_HEIGHT_PX = int(50 * SCALE_FACTOR * SECONDARY_SCALE)

# --- SI Unit Conversion (Scaled) ---
PIXELS_PER_METER = 50 * SCALE_FACTOR
G_METERS_PER_SEC2 = 9.81
GRAVITY_PX_PER_SEC2 = G_METERS_PER_SEC2 * PIXELS_PER_METER

# --- Vector Display (Scaled Arrow Size) ---
VECTOR_SCALE = 0.2
ACCELERATION_VECTOR_SCALE_MULTIPLIER = 0.3
VECTOR_ARROW_SIZE = int(5 * SCALE_FACTOR * SECONDARY_SCALE) # Apply secondary scale

# --- UI Element Dimensions (Scaled + Secondary Scale) ---
BUTTON_WIDTH = int(140 * SCALE_FACTOR * SECONDARY_SCALE)
BUTTON_HEIGHT = int(40 * SCALE_FACTOR * SECONDARY_SCALE)
SMALL_BUTTON_WIDTH = int(30 * SCALE_FACTOR * SECONDARY_SCALE)
SMALL_BUTTON_HEIGHT = int(30 * SCALE_FACTOR * SECONDARY_SCALE)
PAUSE_BUTTON_WIDTH = int(100 * SCALE_FACTOR * SECONDARY_SCALE)
TEXT_BOX_WIDTH = int(120 * SCALE_FACTOR * SECONDARY_SCALE)
TEXT_BOX_HEIGHT = int(30 * SCALE_FACTOR * SECONDARY_SCALE)
# Increase slider dimensions by 20%
SLIDER_SCALE_INCREASE = 1.2
SLIDER_TRACK_WIDTH = int(150 * SCALE_FACTOR * SECONDARY_SCALE * SLIDER_SCALE_INCREASE)
SLIDER_TRACK_HEIGHT = max(1, int(10 * SCALE_FACTOR * SECONDARY_SCALE * SLIDER_SCALE_INCREASE))
SLIDER_HANDLE_WIDTH = max(1, int(10 * SCALE_FACTOR * SECONDARY_SCALE * SLIDER_SCALE_INCREASE))
SLIDER_HANDLE_HEIGHT = max(1, int(20 * SCALE_FACTOR * SECONDARY_SCALE * SLIDER_SCALE_INCREASE))
FORMULA_AREA_HEIGHT = int(120 * SCALE_FACTOR * SECONDARY_SCALE)
SLIDER_AREA_Y_START = FORMULA_AREA_HEIGHT + int(10 * SCALE_FACTOR * SECONDARY_SCALE)
CONTROL_AREA_Y_START = HEIGHT - int(70 * SCALE_FACTOR * SECONDARY_SCALE) # Adjusted offset
# Back Button Configuration
BACK_BUTTON_WIDTH = int(60 * SCALE_FACTOR * SECONDARY_SCALE)
BACK_BUTTON_HEIGHT = int(30 * SCALE_FACTOR * SECONDARY_SCALE)
BACK_BUTTON_TEXT = "< Geri"
# Placement offset for Back Button relative to Circle Y slider
BACK_BUTTON_Y_OFFSET_AFTER_SLIDER = int(45 * SCALE_FACTOR * SECONDARY_SCALE) # Space below the slider label

# --- Default Initial Positions (for Eğik Atış) ---
INITIAL_CIRCLE_OFFSET_X = int(100 * SCALE_FACTOR)
INITIAL_CIRCLE_OFFSET_Y = int(200 * SCALE_FACTOR)
INITIAL_BOX_OFFSET_X = int(250 * SCALE_FACTOR)
INITIAL_BOX_OFFSET_Y = int(200 * SCALE_FACTOR)
# Calculate default positions based on offsets and dimensions
INITIAL_CIRCLE_POS_PX = [float(INITIAL_CIRCLE_OFFSET_X), float(HEIGHT - INITIAL_CIRCLE_OFFSET_Y)]
INITIAL_BOX_POS_PX = [float(WIDTH - INITIAL_BOX_OFFSET_X), float(HEIGHT - INITIAL_BOX_OFFSET_Y)]

# --- Font Sizes (Scaled + Secondary Scale) ---
FONT_SIZE_LARGE = int(32 * SCALE_FACTOR * SECONDARY_SCALE)
FONT_SIZE_MEDIUM = int(28 * SCALE_FACTOR * SECONDARY_SCALE)
FONT_SIZE_SMALL = int(20 * SCALE_FACTOR * SECONDARY_SCALE)
FONT_SIZE_FORMULA = int(26 * SCALE_FACTOR * SECONDARY_SCALE)

# --- UI Padding and Spacing (Scaled + Secondary Scale) ---
PADDING_PX = int(20 * SCALE_FACTOR * SECONDARY_SCALE)
SPACING_PX = int(10 * SCALE_FACTOR * SECONDARY_SCALE)
SLIDER_X_OFFSET = int(50 * SCALE_FACTOR * SECONDARY_SCALE)
SLIDER_Y_SPACING = int(30 * SCALE_FACTOR * SECONDARY_SCALE) # Vertical space between slider tracks
INPUT_BOX_Y_OFFSET = int(5 * SCALE_FACTOR * SECONDARY_SCALE)
FORMULA_CONTROLS_Y_OFFSET = FORMULA_AREA_HEIGHT // 2 - SMALL_BUTTON_HEIGHT // 2
SPEED_MINUS_X_OFFSET = int(100 * SCALE_FACTOR * SECONDARY_SCALE)
SPEED_PLUS_X_OFFSET = int(70 * SCALE_FACTOR * SECONDARY_SCALE)
PAUSE_BUTTON_X_OFFSET = int(100 * SCALE_FACTOR * SECONDARY_SCALE)
INPUT_BOX_BORDER_WIDTH = max(1, int(2 * SCALE_FACTOR * SECONDARY_SCALE))
INPUT_TEXT_X_OFFSET = int(5 * SCALE_FACTOR * SECONDARY_SCALE)
INPUT_TEXT_Y_OFFSET = int(5 * SCALE_FACTOR * SECONDARY_SCALE)
INPUT_LABEL_Y_OFFSET = int(-18 * SCALE_FACTOR * SECONDARY_SCALE)
BUTTON_BORDER_RADIUS = max(1, int(5 * SCALE_FACTOR * SECONDARY_SCALE))
SLIDER_TRACK_BORDER_RADIUS = max(1, int(5 * SCALE_FACTOR * SECONDARY_SCALE))
SLIDER_HANDLE_BORDER_RADIUS = max(1, int(3 * SCALE_FACTOR * SECONDARY_SCALE))
SLIDER_LABEL_Y_OFFSET = int(2 * SCALE_FACTOR * SECONDARY_SCALE) # Space between track bottom and label top
SLIDER_LABEL_COORD_SPACING_X = int(8 * SCALE_FACTOR * SECONDARY_SCALE)
VECTOR_TEXT_OFFSET_X = int(5 * SCALE_FACTOR * SECONDARY_SCALE)
VECTOR_TEXT_OFFSET_Y_UP = int(-15 * SCALE_FACTOR * SECONDARY_SCALE)
VECTOR_TEXT_OFFSET_Y_DOWN = int(5 * SCALE_FACTOR * SECONDARY_SCALE)
VECTOR_COMBINED_OFFSET = int(10 * SCALE_FACTOR * SECONDARY_SCALE)
TIME_TEXT_X_OFFSET = int(10 * SCALE_FACTOR * SECONDARY_SCALE)
TIME_TEXT_Y_OFFSET = int(20 * SCALE_FACTOR * SECONDARY_SCALE)
FORMULA_Y_START = int(10 * SCALE_FACTOR * SECONDARY_SCALE)
FORMULA_COL1_X = int(20 * SCALE_FACTOR * SECONDARY_SCALE)
FORMULA_COL2_X_OFFSET = int(400 * SCALE_FACTOR * SECONDARY_SCALE) # Offset from right
FORMULA_LINE_HEIGHT_MULTIPLIER = 1.1
DRAW_ARROW_LINE_THICKNESS = max(1, int(2 * SCALE_FACTOR * SECONDARY_SCALE))
FORMULA_AREA_LINE_Y_OFFSET = max(1, int(5*SCALE_FACTOR*SECONDARY_SCALE))
FORMULA_AREA_LINE_THICKNESS = max(1, int(1*SCALE_FACTOR*SECONDARY_SCALE))
SCENE_TITLE_Y = 5 # Y position for scene title

# --- Derived UI Calculated Values ---
FORMULA_COL2_X = WIDTH - FORMULA_COL2_X_OFFSET

# Calculate total width of scaled control elements for centering
# Need to define button widths here as they depend on SCALE_FACTOR/SECONDARY_SCALE
TOGGLE_VEC_VIS_BUTTON_WIDTH = int(160 * SCALE_FACTOR * SECONDARY_SCALE)
TOGGLE_VEC_MODE_BUTTON_WIDTH = int(240 * SCALE_FACTOR * SECONDARY_SCALE) # Adjusted for potentially shorter text
TOGGLE_VEC_TYPE_BUTTON_WIDTH = int(200 * SCALE_FACTOR * SECONDARY_SCALE)

TOTAL_CONTROLS_WIDTH = (
    TEXT_BOX_WIDTH + SPACING_PX +
    BUTTON_WIDTH + SPACING_PX +
    BUTTON_WIDTH + SPACING_PX +
    TOGGLE_VEC_VIS_BUTTON_WIDTH + SPACING_PX +
    TOGGLE_VEC_MODE_BUTTON_WIDTH + SPACING_PX +
    TOGGLE_VEC_TYPE_BUTTON_WIDTH
)
CONTROLS_START_X = (WIDTH - TOTAL_CONTROLS_WIDTH) // 2 # Uses scaled WIDTH

# Drawable area height (excluding formula area)
DRAWABLE_HEIGHT = HEIGHT - FORMULA_AREA_HEIGHT
DRAWABLE_Y_OFFSET = FORMULA_AREA_HEIGHT

# --- Scene Configurations ---
SCENES = {
    "Eğik Atış": { # Original slanted throw scene (defaults)
        "title": "Eğik Atış Simülasyonu",
        "initial_projectile_pos": INITIAL_CIRCLE_POS_PX, # Use default calculated positions
        "initial_target_pos": INITIAL_BOX_POS_PX,
        "default_time_str": "2.0",
        "sliders_enabled": ["circle_x", "circle_y", "box_x", "box_y"], # All sliders active
    },
    "Dikey Atış": {
        "title": "Dikey Atış Simülasyonu (Yukarı-Aşağı)",
        "initial_projectile_pos": [WIDTH / 2, HEIGHT - int(100 * SCALE_FACTOR * SECONDARY_SCALE)], # Start centered, lower
        # Target position will be dynamically set to match projectile's initial position
        "initial_target_pos": [WIDTH / 2, HEIGHT - int(100 * SCALE_FACTOR * SECONDARY_SCALE)], # Placeholder, will be overwritten
        "default_time_str": "3.0", # Total flight time
        "sliders_enabled": [], # <<<--- SLIDER KALDIRILDI
    },
    "Yatay Atış": {
        "title": "Yatay Atış Simülasyonu",
        # Start high on the left
        "initial_projectile_pos": [INITIAL_CIRCLE_OFFSET_X, HEIGHT / 3],
        # Target on the ground, further right
        "initial_target_pos": [WIDTH * 0.75, HEIGHT - BOX_HEIGHT_PX - PADDING_PX],
        "default_time_str": "1.0", # Default time (will be recalculated on launch)
        "sliders_enabled": ["circle_x", "circle_y", "box_x", "box_y"], # Enable all sliders
    },
}

# --- Active Scene Selection ---
# Choose which scene configuration to use by default
ACTIVE_SCENE = "Dikey Atış" # Default to the new horizontal throw


# --- Projectile Trail ---
TRAIL_ENABLED = True # Rota çizimi aktif mi?
TRAIL_POINT_INTERVAL_SEC = 0.05 # Saniye cinsinden noktalar arasındaki süre (simülasyon zamanı)
TRAIL_POINT_RADIUS = 2 # Piksel cinsinden iz noktası yarıçapı
TRAIL_POINT_COLOR = LIGHT_GRAY # İz noktası rengi
MAX_TRAIL_POINTS = 200 # Ekranda tutulacak maksimum iz noktası sayısı (performans için)


# --- Peak Height Display ---
PEAK_DOT_ENABLED = True # Tepe noktası bilgisi gösterilsin mi?
PEAK_DOT_COLOR = (255, 60, 60) # Tepe noktası işaretinin rengi (parlak kırmızı)
PEAK_DOT_RADIUS = int(5 * SCALE_FACTOR * SECONDARY_SCALE) # Tepe noktası işaretinin yarıçapı
PEAK_TEXT_COLOR = WHITE # Tepe noktası yazısının rengi
PEAK_TEXT_OFFSET_X = int(8 * SCALE_FACTOR * SECONDARY_SCALE) # Yazının noktadan X ofseti
PEAK_TEXT_OFFSET_Y = int(-8 * SCALE_FACTOR * SECONDARY_SCALE) # Yazının noktadan Y ofseti (yukarı)