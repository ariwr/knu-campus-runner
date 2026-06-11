import random
import pygame

import audio
import game_state as state
from assets_loader import get_room_bg_key
from config import *
from game_data import floors


def player_rect():
    p = state.player
    return pygame.Rect(p["x"], p["y"], p["width"], p["height"])


def set_message(text, frames=120):
    state.message_text = text
    state.message_timer = frames


def get_floor():
    return floors[state.current_floor]


def all_items():
    result = []
    for floor in floors.values():
        for room in floor["rooms"]:
            result.extend(room["items"])
    return result


def count_collected_items():
    items = all_items()
    collected = sum(1 for item in items if item["collected"])
    return collected, len(items)


def all_items_collected():
    items = all_items()
    return len(items) > 0 and all(item["collected"] for item in items)


def move_player(keys, allowed_rect, walls=None):
    if walls is None:
        walls = []

    player = state.player
    moved = False
    dx = 0
    dy = 0

    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        dx -= player["speed"]
        player["facing"] = "left"
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        dx += player["speed"]
        player["facing"] = "right"
    if keys[pygame.K_UP] or keys[pygame.K_w]:
        dy -= player["speed"]
        player["facing"] = "back"
    if keys[pygame.K_DOWN] or keys[pygame.K_s]:
        dy += player["speed"]
        player["facing"] = "front"

    test = player_rect().copy()
    test.x += dx
    if allowed_rect.contains(test) and not any(test.colliderect(w) for w in walls):
        player["x"] += dx
        moved = moved or dx != 0

    test = player_rect().copy()
    test.y += dy
    if allowed_rect.contains(test) and not any(test.colliderect(w) for w in walls):
        player["y"] += dy
        moved = moved or dy != 0

    return moved


def reset_room_students(room):
    room["look_timer"] = 0
    room["next_look_time"] = random.randint(120, 240)
    room["active_looking_student"] = None
    for student in room["students"]:
        student["state"] = "studying"
        student["timer"] = 0


def reset_room_professor(room):
    prof = room.get("professor")
    if prof is None or room.get("kind") != "professor_trap":
        return
    prof["state"] = "teaching"
    prof["sight_offset_x"] = 0.0
    prof["sight_dir"] = 1


def reset_game(show_message=True):
    state.current_floor = 1
    state.current_room = None
    state.return_pos = floors[1]["start"]
    state.game_state = "playing"
    state.caught_reason = ""
    state.caught_animation_timer = 0
    state.dialog_text = ""
    state.dialog_result = None
    state.player["x"], state.player["y"] = floors[1]["start"]
    state.player["facing"] = "front"

    for item in all_items():
        item["collected"] = False

    for floor_no, floor in floors.items():
        for room in floor["rooms"]:
            reset_room_students(room)
            reset_room_professor(room)
        for guard in floor["guards"]:
            guard["rect"].x = 160 if floor_no == 2 else 650
            guard["rect"].y = 490
            guard["dir"] = 1

    if show_message:
        set_message("처음부터 다시 시작합니다.", 120)
    audio.play_background_music()


def trigger_caught(reason):
    state.game_state = "caught"
    state.caught_reason = reason


def trigger_classroom_caught(reason):
    state.caught_reason = reason
    state.game_state = "caught_animation"
    state.caught_animation_timer = 60

    room = state.current_room
    if room is not None:
        if room.get("professor"):
            room["professor"]["state"] = "alert"
        for student in room["students"]:
            student["state"] = "looking"


def change_floor(target_floor):
    state.current_floor = target_floor
    state.current_room = None
    state.game_state = "playing"
    state.player["x"], state.player["y"] = floors[state.current_floor]["start"]
    set_message(f"엘리베이터를 통해 {floors[state.current_floor]['name']}으로 이동했습니다.", 110)


def open_board_menu():
    state.game_state = "board_menu"


def close_board_menu():
    state.game_state = "playing"


def enter_room(room):
    state.current_room = room
    state.return_pos = (state.player["x"], state.player["y"])
    reset_room_students(room)
    reset_room_professor(room)
    state.player["x"] = 500
    state.player["y"] = 540


def exit_room():
    state.current_room = None
    state.player["x"], state.player["y"] = state.return_pos
    set_message("복도로 나왔습니다.", 80)


def elevator_interaction_rect():
    elev = get_floor()["elevator_rect"]
    return pygame.Rect(elev.centerx - 65, 405, 130, 100)


def near_elevator():
    return player_rect().colliderect(elevator_interaction_rect())


def find_near_room():
    p_rect = player_rect()
    for room in get_floor()["rooms"]:
        if p_rect.colliderect(room["entry_rect"]):
            return room
    return None


def room_exit_rect(room=None):
    if room is None:
        room = state.current_room
    if room is not None and get_room_bg_key(room) == "room_classroom":
        return pygame.Rect(830, 235, 120, 170)
    return pygame.Rect(455, 565, 90, 45)


def near_room_exit():
    return player_rect().colliderect(room_exit_rect())


def professor_interaction_rect(room=None):
    if room is None:
        room = state.current_room
    if room is not None and get_room_bg_key(room) == "room_professor":
        return pygame.Rect(390, 285, 270, 115)
    return room["professor"]["rect"].inflate(60, 60)


def near_goal_professor():
    room = state.current_room
    if room is None or room["kind"] != "goal_professor":
        return False
    return player_rect().colliderect(professor_interaction_rect(room))


def start_professor_dialog(text, result):
    state.dialog_text = text
    state.dialog_result = result
    state.game_state = "professor_dialog"


def handle_space_action():
    room = state.current_room

    if room is None:
        if near_elevator():
            open_board_menu()
            return

        near_room = find_near_room()
        if near_room is not None:
            enter_room(near_room)
            return

        set_message("문 앞에서는 방 입장, 엘리베이터 앞에서는 층 이동을 할 수 있습니다.", 110)
        return

    if near_room_exit():
        exit_room()
        return

    if room["kind"] == "goal_professor" and near_goal_professor():
        if all_items_collected():
            start_professor_dialog(room["professor"]["dialog_ready"], "cleared")
        else:
            start_professor_dialog(room["professor"]["dialog_not_ready"], None)
        return

    set_message("문 앞에서는 나가기, 교수님 앞에서는 대화가 가능합니다.", 100)


def guard_light_rect(guard):
    rect = guard["rect"]
    y = rect.centery - GUARD_LIGHT_HEIGHT // 2
    if guard["dir"] == 1:
        return pygame.Rect(rect.right, y, GUARD_LIGHT_LENGTH, GUARD_LIGHT_HEIGHT)
    return pygame.Rect(rect.x - GUARD_LIGHT_LENGTH, y, GUARD_LIGHT_LENGTH, GUARD_LIGHT_HEIGHT)


def update_corridor_guard():
    if state.current_floor == 1:
        return

    for guard in get_floor()["guards"]:
        guard["rect"].x += int(guard["speed"] * guard["dir"])
        if guard["rect"].x < guard["min_x"]:
            guard["rect"].x = guard["min_x"]
            guard["dir"] = 1
        if guard["rect"].x > guard["max_x"]:
            guard["rect"].x = guard["max_x"]
            guard["dir"] = -1

        if player_rect().colliderect(guard["rect"]) or player_rect().colliderect(guard_light_rect(guard)):
            trigger_caught("경비아저씨의 손전등에 걸렸습니다!")
            return


def update_studyroom_students(room, player_moved):
    active = room["active_looking_student"]

    if active is None:
        room["look_timer"] += 1
        if room["students"] and room["look_timer"] >= room["next_look_time"]:
            active = random.choice(room["students"])
            active["state"] = "looking"
            active["timer"] = 0
            room["active_looking_student"] = active
        return

    active["timer"] += 1
    grace = int(FPS * 0.3)
    if player_moved and active["timer"] > grace:
        trigger_caught("뒤돌아본 학생에게 움직이는 모습을 들켰습니다!")
        return

    if active["timer"] >= active["look_duration"]:
        active["state"] = "studying"
        active["timer"] = 0
        room["active_looking_student"] = None
        room["look_timer"] = 0
        room["next_look_time"] = random.randint(120, 240)


def update_professor_sight_sweep(prof):
    prof["sight_offset_x"] += prof["sight_speed"] * prof["sight_dir"]
    if prof["sight_offset_x"] < prof["sight_min_offset_x"]:
        prof["sight_offset_x"] = prof["sight_min_offset_x"]
        prof["sight_dir"] = 1
    if prof["sight_offset_x"] > prof["sight_max_offset_x"]:
        prof["sight_offset_x"] = prof["sight_max_offset_x"]
        prof["sight_dir"] = -1


def professor_sight_points(prof):
    rect = prof["rect"]
    origin = (rect.centerx, rect.bottom - 10)
    offset_x = int(prof.get("sight_offset_x", 0))
    length = prof.get("sight_length", PROFESSOR_SIGHT_LENGTH)
    half_width = prof.get("sight_half_width", PROFESSOR_SIGHT_HALF_WIDTH)
    bottom_center_x = rect.centerx + offset_x
    bottom_y = rect.bottom + length
    left_bottom = (bottom_center_x - half_width, bottom_y)
    right_bottom = (bottom_center_x + half_width, bottom_y)
    return [origin, left_bottom, right_bottom]


def _sign(p1, p2, p3):
    return (p1[0] - p3[0]) * (p2[1] - p3[1]) - (p2[0] - p3[0]) * (p1[1] - p3[1])


def _point_in_triangle(p, a, b, c):
    d1 = _sign(p, a, b)
    d2 = _sign(p, b, c)
    d3 = _sign(p, c, a)
    has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
    has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)
    return not (has_neg and has_pos)


def player_in_professor_sight(prof):
    points = professor_sight_points(prof)
    a, b, c = points
    prect = player_rect()
    check_points = [
        (prect.centerx, prect.centery),
        (prect.left, prect.top),
        (prect.right, prect.top),
        (prect.left, prect.bottom),
        (prect.right, prect.bottom),
    ]
    return any(_point_in_triangle(p, a, b, c) for p in check_points)


def update_room_gimmick(player_moved=False):
    room = state.current_room
    if room is None:
        return

    if room["kind"] == "professor_trap":
        prof = room["professor"]
        update_professor_sight_sweep(prof)
        if player_in_professor_sight(prof):
            trigger_classroom_caught("수업 중인 교수님의 시야에 들어갔습니다!")
            return

    if room["kind"] == "students":
        update_studyroom_students(room, player_moved)


def check_item_collision():
    room = state.current_room
    if room is None:
        return

    for item in room["items"]:
        if not item["collected"] and player_rect().colliderect(item["rect"]):
            item["collected"] = True
            set_message(f"{item['name']} 획득!", 100)


def student_collision_rect(student):
    rect = student["rect"]
    return pygame.Rect(rect.centerx - 36, rect.bottom - 85, 72, 75)


def room_collision_walls(room):
    walls = []
    if state.assets.get(get_room_bg_key(room)) is None:
        walls.extend(room["desks"])
    elif get_room_bg_key(room) == "room_professor":
        walls.append(pygame.Rect(345, 145, 330, 245))
    walls.extend(student_collision_rect(student) for student in room["students"])
    walls.append(pygame.Rect(340, 100, 320, 120))
    return walls
