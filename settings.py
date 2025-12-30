
import os

# Screen dimensions
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SPRITES_DIR = os.path.join(BASE_DIR, 'Sprites')

# Game Settings
PLAYER_SPEED = 5
BULLET_SPEED = 7
ENEMY_SPEED_MIN = 2
ENEMY_SPEED_MAX = 5
METEOR_SPEED_MIN = 1
METEOR_SPEED_MAX = 4
