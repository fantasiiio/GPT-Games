import pygame
from pygame.locals import QUIT, MOUSEBUTTONUP
from GraphicUI import UIPanel, UIButton,UIImage, UILabel
from config import unitSettings
from rectpack import newPacker, PackingMode, SORT_AREA
from rectpack.maxrects import MaxRectsBl
import math
import time

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

class TeamBuilder:
    
    def __init__(self,  player = 1, init_pygame=True, full_screen=False, screen=None):
        self.current_player = player
        # Constants
        self.MAIN_WIDTH = 1500
        self.MAIN_HEIGHT = 1000 
        self.init_graphics(init_pygame, full_screen, screen, self.MAIN_WIDTH, self.MAIN_HEIGHT)

        self.global_id = 1
        self.cash_manager = CashManager(initial_cash=1500, frame_rate=30)
        # UI elements
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 20)
        self.all_rects = None

        self.offsets = {
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

        self.text_offsets = {
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

        self.border_size = 12
        self.units_panel_height = 400
        self.units_panel_width = 800
        self.team_panel_height = 500
        self.button_width = 200
        self.top_panel = UIPanel(0, 0, self.screen_width, 70, border_size=self.border_size)
        self.player_label = self.state_label = UILabel(10, 30, f"Player {self.current_player}", self.top_panel, font_size=60)
        self.player_label.rect.x = self.screen_width / 2 - self.player_label.rect.width / 2
        self.top_panel.add_element(self.player_label)

        self.units_panel = UIPanel(20, self.top_panel.rect.bottom, self.units_panel_width, self.units_panel_height, image="panel.png", border_size=self.border_size)
        self.team_panel = UIPanel(20, self.units_panel.rect.bottom, self.units_panel_width, self.team_panel_height, image="panel.png", border_size=self.border_size)
        self.info_panel = UIPanel(self.units_panel_width+15, self.top_panel.rect.bottom, self.MAIN_WIDTH-self.units_panel_width - 40, self.units_panel_height, image="panel.png", border_size=self.border_size)
        self.unit_properties_panel = UIPanel(self.team_panel.rect.right, self.team_panel.rect.top, self.MAIN_WIDTH - self.team_panel.rect.right - 25, self.team_panel.rect.height, image="panel.png", border_size=self.border_size)
        self.finish_button = UIButton(self.unit_properties_panel.rect.right - self.button_width, self.team_panel.rect.bottom + 5, self.button_width, 50, "Finish", font_size=40, callback=self.button_callback, image="Box03.png", border_size=23)
        remind_text = "Don't forget to add a driver and a gunner for each vehicle" 
        remind_text_image =  self.add_text(self.team_panel, remind_text, (20, 20), font_size=30)
        remind_text_image.rect.bottom = self.team_panel.rect.bottom - 40
        self.main_panel = UIPanel(self.screen_width / 2 - self.MAIN_WIDTH / 2, self.screen_height / 2 - self.MAIN_HEIGHT / 2, self.MAIN_WIDTH, self.MAIN_HEIGHT, image=None, border_size=self.border_size)
        self.main_panel.add_element(self.units_panel)
        self.main_panel.add_element(self.team_panel)
        self.main_panel.add_element(self.info_panel)
        self.main_panel.add_element(self.unit_properties_panel)
        self.main_panel.add_element(self.finish_button)
        self.main_panel.add_element(self.top_panel)

        self.container = (self.team_panel.rect.width - self.border_size*2, self.team_panel.rect.height - self.border_size*2)
        self.packer = newPacker(mode=PackingMode.Offline, pack_algo=MaxRectsBl, sort_algo=SORT_AREA, rotation=False)
        self.packer.add_bin(*self.container)

        self.info_text_image = None
        self.dragging = False
        self.dragged_unit = None
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        self.team_soldier_offset = 0
        self.team_vehicle_offset = 0
        self.cash_manager = CashManager(initial_cash=2000, frame_rate=30)


        # Other state
        self.setting_display_order = [
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
        
        self.unit_over = None
        self.unit = None
        self.outline = None
        self.team_outline = None
        self.team_unit_over = None
        self.team_unit = None
        self.team_dragged_unit = None
        self.selected_team_unit = None
        self.start_drag_offset_x = 0
        self.start_drag_offset_y = 0
        
        # Populate units
        self.populate_units()

    def init_graphics(self, init_pygame, full_screen, screen, width, height):
        self.init_pygame = init_pygame
        if init_pygame:
            pygame.init()
            self.full_screen = full_screen 
            
            # Setup screen
            info = pygame.display.Info()
            if self.full_screen:
                self.screen_width = info.current_w
                self.screen_height = info.current_h
                self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.FULLSCREEN)    
            else:
                self.screen_width = width
                self.screen_height = height
                self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        else:
            self.screen = screen
            self.screen_width = screen.get_width()
            self.screen_height = screen.get_height()  

    def add_text(self, panel, text, pos, font_size=20):
        font = pygame.font.Font(None, font_size)        
        text_surface = font.render(f"{text}", True, (255, 255, 255))
        self.info_text_image = UIImage(pos[0],pos[1], None)
        self.info_text_image.image = text_surface
        panel.add_element(self.info_text_image)
        return self.info_text_image

    def generate_id(self):
            id = self.global_id 
            self.global_id += 1
            return id        
    
    def populate_units(self):
        current_x = 0
        padding_y = 40
        padding_x = 5
        current_y = padding_y

        for setting_name, setting in unitSettings.items():
            if setting_name == "Soldier-Sniper":
                current_x = 0
                current_y = 388 + self.offsets[setting_name][1]
            name = setting_name
            if setting_name.startswith("Soldier-"):
                name = setting_name[8:]
            img = UIImage(current_x + self.offsets[setting_name][0], current_y + self.offsets[setting_name][1], setting["Image"])
            img.id = f"{setting_name}"

            action_pos = (current_x + self.text_offsets[setting_name][0], current_y + self.text_offsets[setting_name][1])
            cost = setting["Purchase Cost"]
            text_surface = self.font.render(f"{name}\n{cost}", True, (255, 255, 255))
            pos_x = img.rect.width / 2 - text_surface.get_width() / 2
            text_image = UIImage(action_pos[0] + pos_x, action_pos[1], None)
            text_image.image = text_surface
            text_image.id = f"txt_{setting_name}"

            current_x += img.image.get_width() + self.offsets[setting_name][0] + padding_x

            self.units_panel.add_element(img)
            self.units_panel.add_element(text_image)
        

    def get_selected_team(self):
        selected_team = []
        for element in self.team_panel.elements:
            if isinstance(element, UIImage):
                if not element.id:
                    continue
                unit_type = self.get_unit_type(element.id)
                selected_team.append(unit_type)
        return selected_team
            
    def run(self):
        
        self.running = True
        
        while self.running:
        
            # Background
            self.vertical_gradient(self.screen, (100, 100, 100), (50, 50, 50))  
            self.main_panel.draw(self.screen)

            for event in pygame.event.get():
                self.main_panel.handle_event(event)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.on_mouse_down(event)
                if event.type == pygame.MOUSEMOTION:
                    self.on_mouse_move(event)
                if event.type == pygame.MOUSEBUTTONUP:
                    self.on_mouse_up(event)
                if event.type == pygame.QUIT:
                    self.running = False

            selected_team_outline = None
            if self.selected_team_unit:
                selected_team_outline = self.get_outline(self.selected_team_unit.image, (0, 255, 0), 1)

            if selected_team_outline:
                self.screen.blit(selected_team_outline, self.selected_team_unit.rect)

            if self.team_outline and self.team_unit_over != self.selected_team_unit:
                self.screen.blit(self.team_outline, self.team_unit_over.rect)
            if self.outline:
                self.screen.blit(self.outline, self.unit_over.rect)
            if self.dragged_unit:
                self.dragged_unit.draw(self.screen)

            # Update cash
            self.cash_manager.update()
            current_cash = self.cash_manager.get_cash()
            self.draw_text(self.screen, f"Cash: {int(current_cash)}", (self.team_panel.rect.right + 20, self.team_panel.rect.y + 20), 60)
            
            pygame.display.flip()
            self.clock.tick(60)
        
        if self.init_pygame:
            pygame.quit()    
        return self.get_selected_team()

    def on_mouse_down(self, event):
        unit = self.mouse_is_over(self.units_panel, event.pos)
        if unit:
            self.dragging = True
            setting = unitSettings[unit.id]
            image_file = setting["Image"]
            img = UIImage(unit.rect.left, unit.rect.top, image_file, move_to_bounding_pos=True)
            img.id = f"{unit.id}-{self.generate_id()}"
            self.dragged_unit = img
            self.drag_offset_x = event.pos[0] - unit.rect.x
            self.drag_offset_y = event.pos[1] - unit.rect.y
            self.dragged_unit.rect.x = event.pos[0] - self.drag_offset_x
            self.dragged_unit.rect.y = event.pos[1] - self.drag_offset_y            

        self.team_unit = self.mouse_is_over_team(event.pos)
        if self.team_unit:
            self.dragging = True
            self.team_dragged_unit = self.team_unit
            self.drag_offset_x = event.pos[0] - self.team_unit.rect.x
            self.drag_offset_y = event.pos[1] - self.team_unit.rect.y
            self.team_unit_rect = self.team_unit.rect.copy()

    def on_mouse_move(self, event):
        self.team_outline = None
        self.outline = None
        #self.team_unit = None
        unit = None

        if self.dragging:
            if self.dragged_unit:
                self.dragged_unit.rect.x = event.pos[0] - self.drag_offset_x
                self.dragged_unit.rect.y = event.pos[1] - self.drag_offset_y
            elif self.team_dragged_unit:
                self.team_dragged_unit.rect.x = event.pos[0] - self.drag_offset_x
                self.team_dragged_unit.rect.y = event.pos[1] - self.drag_offset_y
        else:
            unit = self.mouse_is_over(self.units_panel, event.pos)
            self.team_unit = self.mouse_is_over_team(event.pos)

        if self.team_unit:
            if self.team_unit_over != self.team_unit:
                self.team_unit_over = self.team_unit
                self.write_team_unit_properties(self.team_unit) 
            self.team_outline = self.get_team_outline()
        else:
            self.clear_team_unit_properties()

        if unit:
            if self.unit_over != unit:
                if self.info_text_image in self.info_panel.elements:
                    self.info_panel.elements.clear()
                self.unit_over = unit
                self.write_infos(self.info_panel.rect, self.unit_over)
            self.outline = self.get_outline(self.unit_over.image, (255, 255, 255), 1)
        else: 
            if self.info_text_image in self.info_panel.elements:
                self.unit_over = None
                self.info_panel.elements.clear()            



    def write_team_unit_properties(self, unit):
        pass

    def clear_team_unit_properties(self):
        self.unit_properties_panel.elements.clear()

    def on_mouse_up(self, event):
        if self.dragged_unit and self.team_panel.rect.collidepoint(event.pos):
            self.buy_unit(self.dragged_unit)
            self.dragged_unit = None
            self.dragging = False
        elif self.team_dragged_unit:
            if self.units_panel.rect.collidepoint(event.pos):
                self.team_panel.remove_element(self.team_dragged_unit)
                self.remove_from_packer(self.team_dragged_unit)
                self.update_team_panel()
                unit_type = self.get_unit_type(self.team_dragged_unit.id)
                setting = unitSettings[unit_type]
                cost = setting["Purchase Cost"]
                self.cash_manager.subtract_amount(-cost)                
                self.team_dragged_unit = None
                self.team_unit = None
                self.team_unit_over = None
            elif self.team_unit:
                delta_pos = abs(self.team_dragged_unit.rect.x - self.team_unit_rect.x), abs(self.team_dragged_unit.rect.y - self.team_unit_rect.y)      
                self.team_dragged_unit.rect = self.team_unit_rect   
                self.team_unit = None                     
                if delta_pos[0] < 20 and delta_pos[0] < 20:
                    self.selected_team_unit = self.team_dragged_unit

            elif self.selected_team_unit:
                self.selected_team_unit = None
                self.team_dragged_unit = None

        self.dragging = False
        self.dragged_unit = None
        
    
    def vertical_gradient(self, surface, top_color, bottom_color):
        height = surface.get_height()
        for i in range(height):
            gradient = pygame.Color(0, 0, 0, 0)
            new_rgb = []
            for j in range(3):
                new_rgb.append(int(top_color[j] + (bottom_color[j] - top_color[j]) * i / height))

            gradient.rgb = tuple(new_rgb)
            pygame.draw.line(surface, gradient, (0, i), (surface.get_width(), i))
            
    def button_callback(self, button):
        self.running = False
        
    def remove_from_packer(self, unit):
        packer_rect = (max(unit.bounding_rect.width, 50) + 10, unit.bounding_rect.height, unit.id)    
        self.packer._avail_rect.remove(packer_rect)   
        
    def wrap_text_to_pixel_width(self, text, font, max_width):
        paragraphs = text.split('\n')
        wrapped_paragraphs = []

        for paragraph in paragraphs:
            words = paragraph.split(' ')
            lines = []
            current_line = []
            current_line_width = 0

            for word in words:
                word_width, _ = font.size(word)
                space_width, _ = font.size(' ')

                if current_line_width + word_width + (len(current_line) - 1) * space_width > max_width:
                    lines.append(' '.join(current_line))
                    current_line = []
                    current_line_width = 0

                current_line.append(word)
                current_line_width += word_width

            lines.append(' '.join(current_line))

            # Add tab only to lines after the first one in each paragraph
            wrapped_paragraph = '\n\t'.join(lines)
            wrapped_paragraphs.append(wrapped_paragraph)

        wrapped_text = '\n'.join(wrapped_paragraphs)
        return self.simulate_tab(wrapped_text)
        
    def simulate_tab(self, text, tab_size=4):
        return text.replace("\t", " " * tab_size)
        
    def format_json(self, data):
        formatted_str = ""
        for key in self.setting_display_order:
            if key in data:
                formatted_str += f"{key}: {data[key]}\n"
        return formatted_str

    def get_unit_type(self, id):
        parts = id.rsplit("-", 1)
        return parts[0] if len(parts) > 1 else id

    def write_infos(self, rect, unit):
        font = pygame.font.Font(None, 20)
        font_big = pygame.font.Font(None, 40)
        setting = unitSettings[unit.id]
        formated = self.format_json(setting)

        wrapped_text = self.wrap_text_to_pixel_width(formated, font, rect.width - 40)

        setting = unitSettings[unit.id]
        cost = setting["Purchase Cost"]
        text_unit_type = font_big.render(f"{self.get_unit_type(unit.id)} ({cost})", True, (255, 255, 255))
        text_unit_type_image = UIImage(20,20, None)
        text_unit_type_image.image = text_unit_type

        text_surface = font.render(f"{wrapped_text}", True, (255, 255, 255))
        self.info_text_image = UIImage(20,60, None)
        self.info_text_image.image = text_surface
        self.info_panel.add_element(self.info_text_image)
        self.info_panel.add_element(text_unit_type_image)
        

    def mouse_is_over(self, panel, mouse_pos):
        pos = mouse_pos[0], mouse_pos[1]
        for i in range(len(panel.elements)-1, -1, -1):
            element = panel.elements[i]
            if isinstance(element, UIImage):
                collide = element.rect.collidepoint(pos)
                if collide:
                    return element
        return None
    
    def mouse_is_over_team(self, mouse_pos):
        x, y = mouse_pos
        if not self.all_rects:
            return None
        # Check rects in packed order
        for b, rx, ry, rw, rh, rid in self.all_rects:
            unit = self.find_item_by_id(self.team_panel, rid)
            if unit:
                rect = unit.bounding_rect.copy()                
                rect.x += 20 + rx
                rect.y += 20 + ry
                rect.x += self.team_panel.rect.x
                rect.y += self.team_panel.rect.y
                rect.x += unit.parent.border_size
                rect.y += unit.parent.border_size        
                rect.x -= unit.bounding_rect.x
                rect.y -= unit.bounding_rect.y  
                #pygame.draw.rect(self.screen, (255,0,0), rect, 1)
                if rect.collidepoint(mouse_pos):
                    return unit            

        return None    
    
    def find_item_by_id(self, panel, id):
        for i in range(len(panel.elements)-1, -1, -1):
            element = panel.elements[i]
            if element.id == id:
                return element
        return None
        
    def update_team_panel(self):
        self.packer.pack()
        self.all_rects = self.packer.rect_list()
        for (b, x, y, w, h, rid) in self.all_rects:
            unit = self.find_item_by_id(self.team_panel, rid)
            if unit:
                unit.rect.x = x + 20
                unit.rect.y = y + 20
                unit.set_parent(self.team_panel)
                
    def buy_unit(self, unit):
        unit_type = self.get_unit_type(unit.id)
        setting = unitSettings[unit_type]
        cost = setting["Purchase Cost"]
        if self.cash_manager.get_cash() < cost:
            return False
        self.cash_manager.subtract_amount(cost)
        if unit_type.startswith("Soldier-"):
            unit.rect.x = self.team_soldier_offset
            self.team_soldier_offset += unit.rect.width + 8
            unit.rect.y = 200 + self.offsets[unit_type][1]
        else:
            unit.rect.x = self.team_vehicle_offset
            self.team_vehicle_offset += unit.rect.width + 8
            unit.rect.y = 40 + self.offsets[unit_type][1]


        self.team_panel.add_element(unit)

        self.packer.add_rect(max(unit.bounding_rect.width, 50) + 10, unit.bounding_rect.height, rid=unit.id)
        self.update_team_panel()

        return True
        
    def draw_text(self, surface, text, pos, font_size, color = (255, 255, 255)):
        font = pygame.font.Font(None, font_size)
        text_surface = font.render(text, True, color)
        surface.blit(text_surface, (pos[0] , pos[1]))

    def get_team_outline(self):
        if self.team_unit:
            if self.team_unit_over != self.team_unit:
                self.team_unit_over = self.team_unit
            return self.get_outline(self.team_unit.image, (255, 255, 255), 1)
    

        
if __name__ == "__main__":
    app = TeamBuilder()
    print(app.run())