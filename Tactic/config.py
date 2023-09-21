import json
import random

WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
TILE_SIZE = 64
TILES_X = 22
TILES_Y = 20
GRID_WIDTH = TILE_SIZE * TILES_X
GRID_HEIGHT = TILE_SIZE * TILES_Y
screen = None

STATUS_BAR_WIDTH = 60  # or the width of your soldier sprite
STATUS_BAR_HEIGHT = 6  # adjust based on preference
HEALTH_COLOR = (255, 0, 0)  # Red
POINTS_COLOR = (0, 0, 255)  # Blue
BACKGROUND_COLOR = (200, 200, 200)  # Light gray for depleted sections
SQUARE_SIZE = 5  # adjust based on preference
SQUARE_SPACING = 1  # spacing between squares
MAX_SQUARES_PER_ROW = 10 

unitSettings = None
with open('unitSettings.json', 'r') as file:
    unitSettings = json.load(file)

def speed_to_number(speed_str):
    mapping = {
        "Very Slow": 1,
        "Slow": 2,
        "Medium": 3,
        "Fast": 4,
        "Very Fast": 5
    }
    return mapping.get(speed_str, 0)

def is_number(s):
    try:
        int(s)  # Try converting the string to int (this will work for integers too)
        return True
    except ValueError:
        return False

def get_unit_settings(unit_type): 
    if not is_number(unitSettings[unit_type]["Speed"]):
        unitSettings[unit_type]["Speed"] = speed_to_number(unitSettings[unit_type]["Speed"])
    return unitSettings[unit_type]

maleNames = None
with open('names-male.json', 'r') as file:
    maleNames = json.load(file)
    if maleNames:
        maleNames = maleNames["data"]

def pick_random_name():
    return random.choice(maleNames)
