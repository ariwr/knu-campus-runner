screen = None
assets = {}

font_tiny = None
font_small = None
font_mid = None
font_reason = None
font_big = None
font_huge = None

player = {
    "x": 80,
    "y": 500,
    "width": 30,
    "height": 34,
    "speed": 4,
    "facing": "front",
}

current_floor = 1
current_room = None
return_pos = (80, 500)
game_state = "playing"
message_text = ""
message_timer = 0
caught_reason = ""
caught_animation_timer = 0
dialog_text = ""
dialog_result = None


def setup_runtime(screen_obj, assets_dict, fonts):
    global screen, assets
    global font_tiny, font_small, font_mid, font_reason, font_big, font_huge

    screen = screen_obj
    assets = assets_dict
    font_tiny = fonts["tiny"]
    font_small = fonts["small"]
    font_mid = fonts["mid"]
    font_reason = fonts["reason"]
    font_big = fonts["big"]
    font_huge = fonts["huge"]
