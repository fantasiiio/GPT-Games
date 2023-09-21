import copy
import pygame
from pygame.locals import QUIT, MOUSEBUTTONUP
from GraphicUI import UIPanel, UIButton,UIImage
from config import unitSettings
from rectpack import newPacker, PackingMode, SORT_AREA
from rectpack.maxrects import MaxRectsBl


class CashManager:
    def __init__(self, initial_cash, frame_rate=60):
        self.cash = initial_cash
        self.target_cash = initial_cash
        self.frame_rate = frame_rate
        self.decrease_per_frame = 8
        self.frames_left = 0

    def subtract_amount(self, amount):
        self.target_cash = max(0, self.cash - amount)
        self.frames_left = 1#self.frame_rate  # 1 second = 60 frames at 60 fps
        #self.decrease_per_frame = (self.cash - self.target_cash) / self.frames_left

    def update(self):
        if self.frames_left > 0:
            self.cash -= self.decrease_per_frame
            if self.cash <= self.target_cash:
                self.frames_left = 0
                self.cash = self.target_cash  # To avoid any floating-point errors

    def get_cash(self):
        return self.cash
    
packer = newPacker(mode=PackingMode.Offline, pack_algo=MaxRectsBl, sort_algo=SORT_AREA, rotation=False)
# Assuming UIButton class is defined above...

pygame.init()

# Constants
MAIN_WIDTH = 1500
MAIN_HEIGHT = 800
BACKGROUND_COLOR = (50, 50, 50)

def vertical_gradient(screen, top_color, bottom_color):
    """Draw a vertical gradient from top_color to bottom_color on the given screen."""
    for y in range(screen.get_height()):
        ratio = y / screen.get_height()
        interpolated_color = (
            int(top_color[0] * (1 - ratio) + bottom_color[0] * ratio),
            int(top_color[1] * (1 - ratio) + bottom_color[1] * ratio),
            int(top_color[2] * (1 - ratio) + bottom_color[2] * ratio)
        )
        pygame.draw.line(screen, interpolated_color, (0, y), (screen.get_width(), y))



# Callback function for the button
def button_callback(button):
    print(f"Button {button.text} pressed!")

# Initialization

full_screen = False
info = pygame.display.Info()
screen_width = 0
screen_height = 0
if full_screen:
    screen_width = info.current_w
    screen_height = info.current_h
    screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)    
else:
    screen_width = MAIN_WIDTH
    screen_height = MAIN_HEIGHT
    screen = pygame.display.set_mode((screen_width, screen_height))  

pygame.display.set_caption("UIButton Example")
clock = pygame.time.Clock()

font = pygame.font.Font(None, 15)

# Create a panel and a button
offsets = {
    'Tank': (0, 64),
    'Boat': (-32, 90),
    'Helicopter': (0, -10),
    'Soldier-Bazooka': (0, -64),
    'Soldier-Sniper': (0, -78),
    'Soldier-Pistol': (0, -64),
    'Soldier-Flame Thrower': (0, -64),
    'Soldier-Rifle': (0, -64),
    'Soldier-MachineGun': (0, -64),
    'Soldier-Mecano': (0, -64),
    'Soldier-Medic': (0,-64)
}

text_offsets = {
    'Tank': (0, 60),
    'Boat': (0, 60),
    'Helicopter': (0, -20),
    'Soldier-Bazooka': (0, 0),
    'Soldier-Sniper': (0, 0),
    'Soldier-Pistol': (0, 0),
    'Soldier-Flame Thrower': (0, 0),
    'Soldier-Rifle': (0, 0),
    'Soldier-MachineGun': (0, 0),
    'Soldier-Mecano': (0, 0),
    'Soldier-Medic': (0,0)
}




border_size = 12
units_panel_height = 400
units_panel_width = 650
units_panel = UIPanel(20, 20, units_panel_width, units_panel_height, image="panel.png", border_size=border_size)
team_panel = UIPanel(20, units_panel.rect.bottom, units_panel_width+350, 350, image="panel.png", border_size=border_size)
info_panel = UIPanel(units_panel_width+15, 20, MAIN_WIDTH-units_panel_width - 40, units_panel_height, image="panel.png", border_size=border_size)
unit_preperties_panel = UIPanel(team_panel.rect.right, team_panel.rect.top, MAIN_WIDTH - team_panel.rect.right - 25, team_panel.rect.height, image="panel.png", border_size=border_size)

main_panel = UIPanel(screen_width / 2 - MAIN_WIDTH / 2, screen_height / 2 - MAIN_HEIGHT / 2, MAIN_WIDTH, MAIN_HEIGHT, image=None, border_size=border_size)
main_panel.add_element(units_panel)
main_panel.add_element(team_panel)
main_panel.add_element(info_panel)
main_panel.add_element(unit_preperties_panel)



container = (team_panel.rect.width - border_size*2, team_panel.rect.height - border_size*2)
packer.add_bin(*container)

info_text_image = None
dragging = False
dragged_unit = None
drag_offset_x = 0
drag_offset_y = 0
team_soldier_offset = 0
team_vehicle_offset = 0
cash_manager = CashManager(initial_cash=1000, frame_rate=30)

setting_display_order = [
"Role",
"Strength",
"Weakness",
"Damage",
"Max HP",
"Max AP",
"Max Move Range",
"Max Attack Range",
"Move Cost",  
"Fire Cost",
]

def format_json(data):
    formatted_str = ""
    for key in setting_display_order:
        if key in data:
            formatted_str += f"{key}: {data[key]}\n"
    return formatted_str

def get_unit_type(id):
    parts = id.rsplit("-", 1)
    return parts[0] if len(parts) > 1 else id

def write_infos(rect, unit):
    font = pygame.font.Font(None, 20)
    font_big = pygame.font.Font(None, 40)
    setting = unitSettings[unit.id]
    formated = format_json(setting)

    text_unit_type = font_big.render(f"{get_unit_type(unit.id)}", True, (255, 255, 255))
    text_unit_type_image = UIImage(20,20, None)
    text_unit_type_image.image = text_unit_type

    text_surface = font.render(f"{formated}", True, (255, 255, 255))
    global info_text_image
    info_text_image = UIImage(20,60, None)
    info_text_image.image = text_surface
    info_panel.add_element(info_text_image)    
    info_panel.add_element(text_unit_type_image)
    #print(formated)

def get_outline(image, outline_color, outline_thickness):
    mask = pygame.mask.from_surface(image)
    outline_points = mask.outline()
    outlined_surface = pygame.Surface((image.get_width() + 2 * outline_thickness,
                                    image.get_height() + 2 * outline_thickness),
                                    pygame.SRCALPHA)
    for point in outline_points:
        pygame.draw.circle(outlined_surface, outline_color, (point[0] + outline_thickness, point[1] + outline_thickness), outline_thickness)
    
    #outlined_surface.blit(image, (outline_thickness, outline_thickness))    
    return outlined_surface

def mouse_is_over(units_panel, mouse_pos):
    pos = mouse_pos[0], mouse_pos[1]
    for i in range(len(units_panel.elements)-1, -1, -1):
        element = units_panel.elements[i]
        if isinstance(element, UIImage):
            collide = element.rect.collidepoint(pos)
            if collide:
                return element
    return None

def find_item_by_id(panel, id):
    for i in range(len(panel.elements)-1, -1, -1):
        element = panel.elements[i]
        if element.id == id:
            return element
    return None

all_rects = None
global_id = 1
def buy_unit(unit):
    global team_soldier_offset, team_vehicle_offset, cash_manager
    unit_type = get_unit_type(unit.id)
    setting = unitSettings[unit_type]    
    cost = setting["Purchase Cost"]
    if cash_manager.get_cash() < cost:
        return False    
    cash_manager.subtract_amount(cost)
    name = unit_type
    if unit_type.startswith("Soldier-"):
        name = unit_type[8:]
        unit.rect.x = team_soldier_offset
        team_soldier_offset += unit.rect.width + 8
        unit.rect.y = 200 + offsets[unit_type][1]
    else:
        unit.rect.x = team_vehicle_offset
        team_vehicle_offset += unit.rect.width + 8
        unit.rect.y = 40 + offsets[unit_type][1]


    team_panel.add_element(unit)    

    packer.add_rect(max(unit.bounding_rect.width, 50) + 10, unit.bounding_rect.height, rid=unit.id)
    packer.pack()
    global all_rects
    all_rects = packer.rect_list()
    for (b, x, y, w, h, rid) in all_rects:
        unit = find_item_by_id(team_panel, rid)
        if unit:
            unit.rect.x = x + 20
            unit.rect.y = y + 20
            unit.set_parent(team_panel)

            # unit_type = get_unit_type(unit.id)
            # setting = unitSettings[unit_type]    
            # cost = setting["Purchase Cost"]            
            # text_surface = font.render(f"{unit_type}\n{cost}", True, (255, 255, 255))
            # pos_x = img.bounding_rect.width / 2 - text_surface.get_width() / 2
            # text_image = UIImage(unit.rect.x + pos_x, unit.rect.y, None)
            # text_image.image = text_surface
            # text_image.id = f"txt_{name}"
            # team_panel.add_element(text_image)    

    
    global global_id
    global_id += 1
    return True

current_x = 0
padding_y = 40
padding_x = 5
current_y = padding_y
global_id = 0

for setting_name, setting in unitSettings.items():
    if setting_name == "Soldier-Sniper":
        current_x = 0
        current_y = 388 + offsets[setting_name][1]
    name = setting_name
    if setting_name.startswith("Soldier-"):
        name = setting_name[8:]
    img = UIImage(current_x + offsets[setting_name][0], current_y + offsets[setting_name][1], setting["Image"])
    img.id = f"{setting_name}"

    action_pos = (current_x + text_offsets[setting_name][0], current_y + text_offsets[setting_name][1])
    cost = setting["Purchase Cost"]
    text_surface = font.render(f"{name}\n{cost}", True, (255, 255, 255))
    pos_x = img.rect.width / 2 - text_surface.get_width() / 2
    text_image = UIImage(action_pos[0] + pos_x, action_pos[1], None)
    text_image.image = text_surface
    text_image.id = f"txt_{setting_name}"

    current_x += img.image.get_width() + offsets[setting_name][0] + padding_x

    units_panel.add_element(img)
    units_panel.add_element(text_image)


running = True
unit_over = None
unit = None

def draw_text(surface, text, pos, font_size, color = (255, 255, 255)):
    font = pygame.font.Font(None, font_size)
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, (pos[0] , pos[1]))

while running:
    screen.fill((60, 60, 60))  # Fill background
    
    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN:
            unit = mouse_is_over(units_panel, event.pos)
            if unit:
                dragging = True
                setting = unitSettings[unit.id]                
                image_file = setting["Image"]
                img = UIImage(unit.rect.left, unit.rect.top, image_file, move_to_bounding_pos=True)
                img.id = f"{unit.id}-{global_id+1}"
                dragged_unit = img
                drag_offset_x = event.pos[0] - unit.rect.x
                drag_offset_y = event.pos[1] - unit.rect.y  

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEMOTION:
            if dragging and dragged_unit:
                dragged_unit.rect.x = event.pos[0] - drag_offset_x
                dragged_unit.rect.y = event.pos[1] - drag_offset_y
            else:
                unit = mouse_is_over(units_panel, event.pos) 


        if event.type == pygame.MOUSEBUTTONUP:
            if dragged_unit and team_panel.rect.collidepoint(event.pos):
                buy_unit(dragged_unit)
                dragged_unit = None
                dragging = False
            dragging = False
            dragged_unit = None

    outline = None
    if unit:
        if unit_over != unit:
            if info_text_image in info_panel.elements:
                info_panel.elements.clear()
            unit_over = unit
            write_infos(info_panel.rect, unit_over)
        outline = get_outline(unit_over.image, (255, 255, 255), 1)
    else:
        if info_text_image in info_panel.elements:
            unit_over = None
            info_panel.elements.clear()

    vertical_gradient(screen, (100, 100, 100), (50, 50, 50))  # Draw a gradient background
    main_panel.draw(screen)  # Draw the panel and its child elements
    if outline:
        screen.blit(outline, unit_over.rect)
    if dragged_unit:
        dragged_unit.draw(screen)

    cash_manager.update()
    current_cash = cash_manager.get_cash()        
    draw_text(screen, f"Cash: {int(current_cash)}", (team_panel.rect.right + 20, team_panel.rect.y + 20), 60)
    # if all_rects:
    #     for (b, x, y, w, h, rid) in all_rects:
    #         pygame.draw.rect(screen, (255, 0, 0), (x +team_panel.rect.x , y+team_panel.rect.y, w, h), 1)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()




