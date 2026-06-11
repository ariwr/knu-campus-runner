import os

import pygame

from config import CLASSROOM_ROOM_IDS


def load_image(path, size=None, alpha=True):
    full_path = os.path.join(os.path.dirname(__file__), path)
    image = pygame.image.load(full_path).convert_alpha() if alpha else pygame.image.load(full_path).convert()
    if size is not None:
        image = pygame.transform.scale(image, size)
    return image


def safe_load_image(path, size=None, alpha=True):
    try:
        return load_image(path, size, alpha)
    except Exception:
        return None


def load_assets():
    base = "assets/cropped_game_assets"
    return {
        "player_front": safe_load_image("assets/player/processed/player_front.png"),
        "player_back": safe_load_image("assets/player/processed/player_back.png"),
        "player_left": safe_load_image("assets/player/processed/player_left.png"),
        "player_right": safe_load_image("assets/player/processed/player_right.png"),
        "professor": safe_load_image(f"{base}/sprites_transparent/professor.png"),
        "professor_classroom": safe_load_image("assets/professor/classroom_professor_clean.png"),
        "professor_classroom_angry": safe_load_image("assets/professor/classroom_professor_angry_clean.png"),
        "student": safe_load_image(f"{base}/sprites_transparent/student.png"),
        "boy_studyroom": safe_load_image("assets/students/boys_studyroom.png"),
        "boy_studyroom_look": safe_load_image("assets/students/boys_surprise_studyroom.png"),
        "girl_studyroom": safe_load_image("assets/students/girls_studyroom.png"),
        "girl_studyroom_look": safe_load_image("assets/students/girls_surprise_studyroom.png"),
        "boy_classroom": safe_load_image("assets/students/boys_classroom.png"),
        "boy_classroom_look": safe_load_image("assets/students/boys_surprise_classroom.png"),
        "girl_classroom": safe_load_image("assets/students/girls_classroom.png"),
        "girl_classroom_look": safe_load_image("assets/students/girls_surprise_classroom.png"),
        "guard": safe_load_image(f"{base}/sprites_transparent/guard.png"),
        "guard_left": safe_load_image("assets/security/security_left.png"),
        "guard_right": safe_load_image("assets/security/security_right.png"),
        "board": safe_load_image(f"{base}/sprites_transparent/bulletin_board.png", (140, 80)),
        "elevator": safe_load_image(f"{base}/sprites_transparent/elevator_object.png", (78, 112)),
        "door": safe_load_image(f"{base}/sprites_transparent/door_object.png", (48, 60)),
        "teacher_desk": safe_load_image(f"{base}/sprites_transparent/teacher_desk_object.png", (95, 50)),
        "student_desk": safe_load_image(f"{base}/sprites_transparent/student_desk_object.png", (95, 38)),
        "item_variable": safe_load_image("assets/items/item_variable_note.png"),
        "item_condition": safe_load_image("assets/items/item_conditional_card.png"),
        "item_loop": safe_load_image("assets/items/item_loop_badge.png"),
        "item_function": safe_load_image("assets/items/item_function_key.png"),
        "item_list": safe_load_image("assets/items/item_list_piece.png"),
        "item_dict": safe_load_image("assets/items/item_dictionary_map.png"),
        "tile_corridor": safe_load_image(f"{base}/map_tiles/corridor_tile.png"),
        "tile_corridor_floor": safe_load_image(f"{base}/map_tiles/corridor_tile_floor.png"),
        "tile_classroom": safe_load_image(f"{base}/map_tiles/classroom_tile.png"),
        "tile_classroom_floor": safe_load_image(f"{base}/map_tiles/classroom_tile_floor.png"),
        "tile_auditorium": safe_load_image(f"{base}/map_tiles/auditorium_tile.png"),
        "tile_wall": safe_load_image(f"{base}/map_tiles/wall_tile.png"),
        "passageway_1": safe_load_image("assets/passageway/1st_floor.png", alpha=False),
        "passageway_2": safe_load_image("assets/passageway/2nd_floor.png", alpha=False),
        "passageway_3": safe_load_image("assets/passageway/3rd_floor.png", alpha=False),
        "room_classroom": safe_load_image("assets/rooms/classroom.png", alpha=False),
        "room_professor": safe_load_image("assets/rooms/professor_room.png", alpha=False),
        "room_studyroom": safe_load_image("assets/rooms/studyroom.png", alpha=False),
    }


ITEM_IMAGE_MAP = {
    "변수 노트": "item_variable",
    "조건문 카드": "item_condition",
    "반복문 배지": "item_loop",
    "함수 열쇠": "item_function",
    "리스트 조각": "item_list",
    "딕셔너리 지도": "item_dict",
}


def get_room_bg_key(room):
    if room["kind"] == "goal_professor":
        return "room_professor"
    if room["id"] in CLASSROOM_ROOM_IDS:
        return "room_classroom"
    return "room_studyroom"
