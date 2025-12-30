
import os

# Screen dimensions
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
FULLSCREEN = False  # Toggle fullscreen mode

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# UI Color Palette
UI_PRIMARY = (100, 200, 255)  # Bright cyan
UI_SECONDARY = (50, 100, 200)  # Deep blue
UI_ACCENT = (255, 200, 50)  # Gold
UI_SUCCESS = (50, 255, 100)  # Bright green
UI_DANGER = (255, 50, 50)  # Bright red
UI_TEXT = (255, 255, 255)  # White
UI_TEXT_DIM = (150, 150, 150)  # Gray
UI_BG_DARK = (10, 10, 30)  # Very dark blue
UI_BG_OVERLAY = (0, 0, 0, 180)  # Semi-transparent black

# Gradient colors
HEALTH_GRADIENT_HIGH = (50, 255, 100)
HEALTH_GRADIENT_MID = (255, 200, 50)
HEALTH_GRADIENT_LOW = (255, 50, 50)

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SPRITES_DIR = os.path.join(BASE_DIR, 'Sprites')
AUDIO_DIR = os.path.join(BASE_DIR, 'Audio')
BG_MUSIC_PATH = os.path.join(AUDIO_DIR, 'bg_music.mp3')
COLLISION_SOUND_PATH = os.path.join(AUDIO_DIR, 'collision.mp3')

# Game Settings
PLAYER_SPEED = 5
BULLET_SPEED = 7
ENEMY_SPEED_MIN = 2
ENEMY_SPEED_MAX = 5
METEOR_SPEED_MIN = 1
METEOR_SPEED_MAX = 4

# UI Animation Settings
BUTTON_HOVER_SCALE = 1.1
BUTTON_CLICK_SCALE = 0.95
FADE_SPEED = 3.0  # Opacity change per second
PULSE_SPEED = 2.0  # Pulse cycles per second
SCORE_POPUP_DURATION = 1.0  # seconds

# Visual Effects Settings
SCREEN_SHAKE_TRAUMA = 0.3  # Amount of trauma for collisions
PARTICLE_COUNT_EXPLOSION = 20
PARTICLE_COUNT_STARS = 150
