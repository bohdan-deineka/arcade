__author__ = "Bohdan Deineka, Bartlomiej Matuszewski, Bartlomiej Kuzba"
__copyright__ = "Copyright 2020, The Arcade Project"
__credits__ = ["Bohdan Deineka", "Bartlomiej Matuszewski", "Bartlomiej Kuzba"]
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Bohdan Deineka"
__email__ = "bohdan.deineka@edu.uni.lodz.pl"
__status__ = "Production"

# Constants
SCREEN_WIDTH = 720
SCREEN_HEIGHT = 480
SCREEN_TITLE = "Platformer"
MUSIC_VOLUME = 0.5

CHARACTER_SCALING = 0.5
TILE_SCALING = 1
COIN_SCALING = 1
SPRITE_PIXEL_SIZE = 128
GRID_PIXEL_SIZE = (SPRITE_PIXEL_SIZE * TILE_SCALING)

PLAYER_MOVEMENT_SPEED = 5
GRAVITY = 2
PLAYER_JUMP_SPEED = 20

# How many pixels to keep as a minimum margin between the character
# and the edge of the screen.
LEFT_VIEWPORT_MARGIN = 0
RIGHT_VIEWPORT_MARGIN = 100
BOTTOM_VIEWPORT_MARGIN = 100
TOP_VIEWPORT_MARGIN = 100

PLAYER_START_X = 8
PLAYER_START_Y = 192

