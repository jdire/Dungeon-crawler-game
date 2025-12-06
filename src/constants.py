"""Game constants"""

import math

# Development settings
DEV_MODE = True  # Set to False for production builds

# Screen settings
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

# Raycasting settings
FOV = math.pi / 3  # 60 degrees field of view
HALF_FOV = FOV / 2
NUM_RAYS = 120  # Number of rays to cast
MAX_DEPTH = 20  # Maximum ray distance
DELTA_ANGLE = FOV / NUM_RAYS

# Player settings
PLAYER_SPEED = 2.0
ROTATION_SPEED = 0.05

# Map settings
TILE_SIZE = 64

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Wall types
WALL = 1
EMPTY = 0
