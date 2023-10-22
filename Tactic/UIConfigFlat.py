from config import base_path
# from GraphicUI import AUTO

ui_settings_flat ={
    "UIButton":{
        "image":f"{base_path}\\assets\\UI-v2\\Buttons\\Framed\\Square\\Green\\Button_FSG_Background.png",
        "border_size":12,
        "text_color": (216,241,180),
        "font_size": 30,
        "hover_text_color": (255,255,255),
        "height": 64,
        "width": 100,
        "padding": 14,
        "horizontal_align":'center',
        "font_path": f"{base_path}\\assets\\Fonts\\KozGoPro-Regular.ttf",
        "hover_image":f"{base_path}\\assets\\UI-v2\\Buttons\\Framed\\Square\\Green\\Outline.png",
    },
    "UIContainer":{
        "image":None,
        "border_size":0,
        "padding": 20,
        "height": 100,
        "width": 100,
        "min_width": 0,
        "min_height": 0,
        "horizontal_align":'center',
        "no_image_color": (44, 65, 81, 255)
    },
    "UIHeader":{
        "image":f"{base_path}\\assets\\UI-v2\\Window\\Window_Header.png",
        "border_size":24,
        "horizontal_align":'left',
        "num_columns": 1,
        "padding": 20,
        "text_color": (200, 200, 200),
        "font_size": 40,
        "height": 50
    },
    "UITextBox":{
        "image":f"{base_path}\\assets\\UI-v2\\Input\\Input_Background.png",
        "image_focus":f"{base_path}\\assets\\UI-v2\\Input\\Input_Focus.png",
        "border_size":12,
        "padding": 10,
        "text_color": (166,199,80),
        "font_size": 30,
        "width": 100,
        "height": 40,
        "cursor_color": (255,255,255),
        "enable_color_picker": False,
        "selection_color":  (200, 233, 114),
    },
    "UIPopupBase":{
        "header_height": 94,
        "header_width": 250,
        "header_offset_x": -23,
        "header_offset_y": 64,
        "ok_button_image":f"{base_path}\\assets\\UI-v2\\Buttons\\Framed\\Square\\Green\\Icons\\Accept.png",
        "cancel_button_image":f"{base_path}\\assets\\UI-v2\\Buttons\\Framed\\Square\\Green\\Icons\\Decline.png",
        "padding_header": 30
    },
    "UILabel":{
        "text_color": (166,199,80),
        "font_size": 30,
        "padding": 0,
        "outline_width": 0,
        "outline_color": (0,0,0),
        "font_path": f"{base_path}\\assets\\Fonts\\arial.ttf"
    },
    "UIProgressBar":{
        "image": None,
        "border_size": 0,
        "padding": 0,
        "width": 100,
        "height": 10,
        "color1": (0,255,0),
        "color2": (200,200,200),
        "max_squares_per_row": 5,
        "max_value": 5,
        "square_height": 10,
    },
    "UIList":{
        "num_columns": 1,
        "item_height": None,
        "width": 0,
        "height": 0,
        "padding": 20,
        "image":f"{base_path}\\assets\\UI-v2\\Window\\Window.png",
        "header_border_size": 24,
        "border_size": 80,
        "header_height": None,
        "enable_scrollbar": True,
        "item_height": 50,
        "header_image":f"{base_path}\\assets\\UI-v2\\Window\\Window_small.png",
    },
    "UIScrollBar":{
        "image":f"{base_path}\\assets\\UI-v2\\Sliders & Scrollbars\\Scrollbar_Vertical_Background.png",
        "caret_image":f"{base_path}\\assets\\UI-v2\\Sliders & Scrollbars\\Scrollbar_Vertical_Thumb.png",
        "border_size": 6,
        "padding": 0,
        "color": (0,0,0)
    },

}