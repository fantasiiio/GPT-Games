import pygame
import requests
from io import BytesIO
import json
import random
from enum import Enum

email_sender = "fredericgiroux666@gmail.com"
email_sender_password = "ughi hfbp pzdk bfzp"

base_path = "C:\\dev-fg\\GPT-Games\\Tactic"

WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
TILE_SIZE = 64
TILES_X = 22
TILES_Y = 20
GRID_WIDTH = TILE_SIZE * TILES_X
GRID_HEIGHT = TILE_SIZE * TILES_Y
screen = None
server_ip = "127.0.0.1"
server_port = 65432


STATUS_BAR_WIDTH = 60  # or the width of your soldier sprite
STATUS_BAR_HEIGHT = 6  # adjust based on preference
HEALTH_COLOR = (255, 0, 0)  # Red
POINTS_COLOR = (0, 0, 255)  # Blue
BACKGROUND_COLOR = (200, 200, 200)  # Light gray for depleted sections
SQUARE_SIZE = 5  # adjust based on preference
SQUARE_SPACING = 1  # spacing between squares
MAX_SQUARES_PER_ROW = 10 
    
redis_host = "redis-15293.c228.us-central1-1.gce.cloud.redislabs.com"
redis_port = 15293
unitSettings = None
with open('C:\\dev-fg\\GPT-Games\\Tactic\\data\\unitSettings.json', 'r') as file:
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
with open(f"{base_path}\\data\\names-male.json", 'r') as file:
    maleNames = json.load(file)
    if maleNames:
        maleNames = maleNames["data"]

def pick_random_name():
    return random.choice(maleNames)

GameStateString = {
    "UNIT_PLACEMENT": "Unit Placement",
    "RANDOM_EVENT": "Random Event",
    "PLANNING": "Planning",
    "EXECUTION": "Execution",
    "OUTCOME": "Outcome"
}

def find_object_by_property(array, property_name, value):
    for obj in array:
        if obj[property_name] == value:
            return obj
    return None

country_names = None
with open(f"{base_path}\\data\\country-names.json", 'r') as file:
    country_names = json.load(file)

countries = None
with open(f"{base_path}\\data\\countries.json", 'r') as file:
    countries = json.load(file)
    if countries and country_names:
        for country in countries:
            country_name = find_object_by_property(country_names, "let3",  country["alpha3"])
            if country_name:
                country["alpha2"] = country_name["let2"]

def load_image_from_url(url):
    response = requests.get(url)
    if response.status_code == 200:  # Check if request was successful
        image_data = BytesIO(response.content)
        return pygame.image.load(image_data)
    else:
        print(f"Failed to load image from {url}. Status code: {response.status_code}")
        return None
    
image_cache = {}

def get_country_image(alpha2):
    # Check if the image is already in the cache
    if alpha2 in image_cache:
        return image_cache[alpha2]

    # Otherwise, load the image from the URL and store it in the cache
    for country in countries:
        if "alpha2" in country and country["alpha2"] == alpha2:
            image = pygame.image.load(f"{base_path}\\data\\flags\\{country['name']}.png")
            if image:  # Store only if the image was successfully loaded
                image_cache[alpha2] = image
            return image
        

class GameState(Enum):
    UNIT_PLACEMENT = 1
    RANDOM_EVENT = 2
    PLANNING = 3
    EXECUTION = 4
    OUTCOME = 5

# class GameStateTeamBuilder(Enum):
#     UNIT_PLACEMENT = 1
#     RANDOM_EVENT = 2
#     PLANNING = 3
#     EXECUTION = 4
#     OUTCOME = 5    

user_settings = None
with open(f"{base_path}\\data\\player.json", 'r') as file:
    user_settings = json.load(file)

def save_user_settings():
    with open(f"{base_path}\\data\\player.json", 'w') as file:
        json.dump(user_settings, file, indent=4)

fake_users = None
with open(f"{base_path}\\data\\fake_users.json", 'r') as file:
    fake_users = json.load(file)