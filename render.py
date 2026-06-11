import pygame

import game_state as state
import mechanics
from assets_loader import ITEM_IMAGE_MAP, get_room_bg_key
from config import *


def draw_text(text, x, y, font, color=BLACK, center=False):
    surf = font.render(text, True, color)
    rect = surf.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    state.screen.blit(surf, rect)


def draw_overlay(alpha, height=SCREEN_HEIGHT, y=0):
    overlay = pygame.Surface((SCREEN_WIDTH, height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, alpha))
    state.screen.blit(overlay, (0, y))


def draw_tiled(tile_img, dest_rect, tile_size=None):
    if tile_size is not None:
        tile_img = pygame.transform.scale(tile_img, tile_size)

    tw = tile_img.get_width()
    th = tile_img.get_height()
    old_clip = state.screen.get_clip()
    state.screen.set_clip(dest_rect)
    for ty in range(dest_rect.y, dest_rect.bottom, th):
        for tx in range(dest_rect.x, dest_rect.right, tw):
            state.screen.blit(tile_img, (tx, ty))
    state.screen.set_clip(old_clip)


def draw_player():
    rect = mechanics.player_rect()
    facing = state.player.get("facing", "front")
    src = state.assets.get(f"player_{facing}") or state.assets.get("player")

    if src:
        disp_w = (rect.width + 14) * 3
        disp_h = disp_w * src.get_height() // src.get_width()
        img = pygame.transform.scale(src, (disp_w, disp_h))
        state.screen.blit(img, (rect.centerx - disp_w // 2, rect.bottom - disp_h))
    else:
        pygame.draw.rect(state.screen, BLUE, rect)
        pygame.draw.rect(state.screen, BLACK, rect, 2)
        draw_text("P", rect.centerx, rect.centery + 1, state.font_small, WHITE, center=True)


def draw_item(item):
    if item["collected"]:
        return

    key = ITEM_IMAGE_MAP.get(item["name"])
    img = state.assets.get(key)

    if img:
        scale = min(ITEM_DRAW_SIZE / img.get_width(), ITEM_DRAW_SIZE / img.get_height())
        disp_w = max(1, int(img.get_width() * scale))
        disp_h = max(1, int(img.get_height() * scale))
        scaled = pygame.transform.scale(img, (disp_w, disp_h))
        draw_rect = scaled.get_rect(center=item["rect"].center)
        state.screen.blit(scaled, draw_rect.topleft)
    else:
        pygame.draw.rect(state.screen, item["color"], item["rect"], border_radius=5)
        pygame.draw.rect(state.screen, BLACK, item["rect"], 2, border_radius=5)
        draw_text(item["symbol"], item["rect"].centerx, item["rect"].centery, state.font_small, BLACK, center=True)

    draw_text(item["name"], item["rect"].centerx, item["rect"].y - 24, state.font_tiny, BLACK, center=True)


def draw_ui():
    count, total = mechanics.count_collected_items()
    screen = state.screen

    pygame.draw.rect(screen, (25, 35, 55), (0, 0, SCREEN_WIDTH, 54))
    location = mechanics.get_floor()["name"]
    if state.current_room is not None:
        location += f" / {state.current_room['name']}"
    draw_text(f"현재 위치: {location}", 20, 15, state.font_mid, WHITE)

    item_text = f"Python 개념 아이템: {count} / {total}"
    item_surf = state.font_mid.render(item_text, True, WHITE)
    item_rect = item_surf.get_rect(topright=(980, 15))
    screen.blit(item_surf, item_rect)

    if total > 0 and count == total and state.game_state == "playing":
        notice_text = "모든 아이템을 모았습니다! 3층 교수실로 찾아가세요."
        notice_surf = state.font_mid.render(notice_text, True, PURPLE)
        notice_rect = notice_surf.get_rect(center=(500, 78)).inflate(64, 22)
        pygame.draw.rect(screen, (255, 250, 225), notice_rect, border_radius=8)
        pygame.draw.rect(screen, PURPLE, notice_rect, 2, border_radius=8)
        screen.blit(notice_surf, notice_surf.get_rect(center=notice_rect.center))

    if state.message_text:
        msg_rect = pygame.Rect(150, 592, 700, 42)
        pygame.draw.rect(screen, (255, 250, 225), msg_rect, border_radius=8)
        pygame.draw.rect(screen, DARK_GRAY, msg_rect, 2, border_radius=8)
        draw_text(state.message_text, 500, 613, state.font_small, RED, center=True)


def draw_debug_hitboxes():
    if not DEBUG_HITBOX:
        return

    if state.current_room is None:
        for room in mechanics.get_floor()["rooms"]:
            pygame.draw.rect(state.screen, (0, 120, 255), room["door_rect"], 2)
            pygame.draw.rect(state.screen, (0, 255, 80), room["entry_rect"], 2)
        pygame.draw.rect(state.screen, (255, 230, 0), mechanics.elevator_interaction_rect(), 2)


def room_visual_rect(index):
    xs = [65, 200, 335, 580, 715, 850]
    return pygame.Rect(xs[index], 95, 110, 140)


def draw_corridor():
    floor = mechanics.get_floor()
    pw_key = f"passageway_{state.current_floor}"
    has_passageway_bg = state.assets.get(pw_key) is not None

    if has_passageway_bg:
        bg = pygame.transform.scale(state.assets[pw_key], (SCREEN_WIDTH, SCREEN_HEIGHT))
        state.screen.blit(bg, (0, 0))
    else:
        draw_simple_corridor(floor)

    if state.current_floor >= 2:
        for guard in floor["guards"]:
            draw_guard(guard)

    draw_debug_hitboxes()
    draw_player()
    draw_ui()


def draw_simple_corridor(floor):
    state.screen.fill(LIGHT_GRAY)
    hall_rect = pygame.Rect(45, 250, 910, 320)
    floor_tile = state.assets.get("tile_corridor_floor") or state.assets.get("tile_corridor")
    if floor_tile:
        draw_tiled(floor_tile, hall_rect)
    else:
        pygame.draw.rect(state.screen, HALL_FLOOR, hall_rect)
    pygame.draw.rect(state.screen, DARK_GRAY, hall_rect, 4)

    for i, room in enumerate(floor["rooms"]):
        visual = room_visual_rect(i)
        color = ROOM_SAFE if room["kind"] == "empty" else (225, 230, 242)
        if room["kind"] == "professor_trap":
            color = (242, 225, 225)
        if room["kind"] == "goal_professor":
            color = (230, 222, 205)

        pygame.draw.rect(state.screen, color, visual)
        pygame.draw.rect(state.screen, ROOM_WALL, visual, 3)
        pygame.draw.rect(state.screen, BROWN, room["door_rect"])
        pygame.draw.rect(state.screen, BLACK, room["door_rect"], 2)
        draw_text(room["id"] + "호", visual.centerx, visual.y + 18, state.font_mid, BLACK, center=True)

    board = floor["board_rect"]
    pygame.draw.rect(state.screen, BOARD_BROWN, board)
    pygame.draw.rect(state.screen, BLACK, board, 3)
    draw_text("게시판", board.centerx, board.y - 28, state.font_mid, BLACK, center=True)

    elev = floor["elevator_rect"]
    pygame.draw.rect(state.screen, SKY, elev)
    pygame.draw.rect(state.screen, BLACK, elev, 3)
    draw_text("엘리베이터", elev.centerx, elev.y - 24, state.font_small, BLACK, center=True)


def draw_blackboard():
    pygame.draw.rect(state.screen, BLACKBOARD, (350, 105, 300, 70))
    pygame.draw.rect(state.screen, DARK_BROWN, (350, 105, 300, 70), 5)
    draw_text("Python", 500, 140, state.font_mid, WHITE, center=True)


def draw_desk(rect):
    if state.assets.get("student_desk"):
        img = pygame.transform.scale(state.assets["student_desk"], (rect.width, rect.height + 10))
        state.screen.blit(img, (rect.x, rect.y - 5))
    else:
        pygame.draw.rect(state.screen, BROWN, rect, border_radius=4)
        pygame.draw.rect(state.screen, DARK_BROWN, rect, 2, border_radius=4)


def draw_professor(rect, surprised=False):
    if state.assets.get("professor"):
        src = state.assets["professor"]
        disp_w = rect.width + 16
        disp_h = disp_w * src.get_height() // src.get_width()
        img = pygame.transform.scale(src, (disp_w, disp_h))
        state.screen.blit(img, (rect.centerx - disp_w // 2, rect.bottom - disp_h))
    else:
        pygame.draw.rect(state.screen, (60, 60, 80), rect)
        pygame.draw.rect(state.screen, BLACK, rect, 2)
    if surprised:
        draw_text("!", rect.centerx + 30, rect.y - 25, state.font_big, RED, center=True)


def draw_classroom_professor(prof):
    is_alert = prof.get("state") == "alert" or state.game_state == "caught_animation"
    image_key = prof.get("alert_image_key") if is_alert else prof.get("normal_image_key")
    src = state.assets.get(image_key) or state.assets.get("professor")
    rect = prof["rect"]

    if src:
        bbox = src.get_bounding_rect()
        if bbox.width > 0 and bbox.height > 0:
            src = src.subsurface(bbox)
        disp_w = prof.get("draw_width", PROFESSOR_DRAW_WIDTH)
        disp_h = disp_w * src.get_height() // src.get_width()
        img = pygame.transform.scale(src, (disp_w, disp_h))
        offset_x = prof.get("sprite_offset_x", 0)
        offset_y = prof.get("sprite_offset_y", 0)
        draw_rect = img.get_rect()
        draw_rect.midbottom = (rect.centerx + offset_x, rect.bottom + offset_y)
        state.screen.blit(img, draw_rect.topleft)
    else:
        pygame.draw.rect(state.screen, (60, 60, 80), rect)
        pygame.draw.rect(state.screen, BLACK, rect, 2)


def draw_professor_sight(prof):
    points = mechanics.professor_sight_points(prof)
    sight_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    pygame.draw.polygon(sight_surface, (255, 80, 80, 55), points)
    state.screen.blit(sight_surface, (0, 0))


def draw_student(student):
    rect = student["rect"]
    is_looking = student.get("state") == "looking"
    src = state.assets.get(student["look_image_key"] if is_looking else student["normal_image_key"])
    if src is None:
        src = state.assets.get("student")

    if src:
        scale_factor = 1.0
        if student["normal_image_key"].startswith("girl_"):
            scale_factor = STUDENT_GIRL_LOOK_DRAW_SCALE if is_looking else STUDENT_GIRL_DRAW_SCALE
        disp_w = int(STUDENT_DRAW_WIDTH * scale_factor)
        disp_h = disp_w * src.get_height() // src.get_width()
        img = pygame.transform.scale(src, (disp_w, disp_h))
        state.screen.blit(img, (rect.centerx - disp_w // 2, rect.bottom - disp_h))
    else:
        color = ORANGE if is_looking else (70, 90, 130)
        pygame.draw.rect(state.screen, color, rect)
        pygame.draw.rect(state.screen, BLACK, rect, 2)

    if is_looking:
        draw_text("!", rect.centerx + 24, rect.y - 28, state.font_big, RED, center=True)


def draw_room():
    room = state.current_room
    room_bg_key = get_room_bg_key(room)
    has_room_bg = state.assets.get(room_bg_key) is not None

    if has_room_bg:
        bg = pygame.transform.scale(state.assets[room_bg_key], (SCREEN_WIDTH, SCREEN_HEIGHT))
        state.screen.blit(bg, (0, 0))
    else:
        draw_simple_room(room)

    exit_rect = mechanics.room_exit_rect(room)
    if room_bg_key != "room_classroom":
        pygame.draw.rect(state.screen, BROWN, exit_rect)
        pygame.draw.rect(state.screen, BLACK, exit_rect, 2)
        draw_text("나가기", exit_rect.centerx, exit_rect.centery, state.font_small, WHITE, center=True)

    if not has_room_bg:
        for desk in room["desks"]:
            draw_desk(desk)

    if room["kind"] == "professor_trap":
        draw_professor_sight(room["professor"])
    elif room["kind"] == "goal_professor":
        prof = room["professor"]
        if room_bg_key != "room_professor":
            draw_professor(prof["rect"], surprised=mechanics.all_items_collected())

    for student in room["students"]:
        draw_student(student)

    if room["kind"] == "professor_trap":
        draw_classroom_professor(room["professor"])

    for item in room["items"]:
        draw_item(item)

    draw_player()
    draw_ui()


def draw_simple_room(room):
    state.screen.fill((225, 225, 225))
    room_area = pygame.Rect(80, 90, 840, 490)
    floor_tile = state.assets.get("tile_classroom_floor") or state.assets.get("tile_classroom")
    if floor_tile:
        draw_tiled(floor_tile, room_area)
    else:
        pygame.draw.rect(state.screen, ROOM_FLOOR, room_area)
    pygame.draw.rect(state.screen, DARK_GRAY, room_area, 4)
    draw_blackboard()
    if room["kind"] in ["professor_trap", "goal_professor"]:
        pygame.draw.rect(state.screen, (160, 95, 55), (405, 180, 190, 35))
        pygame.draw.rect(state.screen, DARK_BROWN, (405, 180, 190, 35), 2)


def draw_guard(guard):
    light = mechanics.guard_light_rect(guard)
    rect = guard["rect"]
    light_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)

    if guard["dir"] == 1:
        points = [(rect.right, rect.centery), (light.right, light.y), (light.right, light.bottom)]
    else:
        points = [(rect.left, rect.centery), (light.left, light.y), (light.left, light.bottom)]
    pygame.draw.polygon(light_surface, (*LIGHT_CONE, 90), points)
    state.screen.blit(light_surface, (0, 0))

    src = state.assets.get("guard_right" if guard["dir"] == 1 else "guard_left") or state.assets.get("guard")
    if src:
        bbox = src.get_bounding_rect()
        if bbox.width > 0 and bbox.height > 0:
            src = src.subsurface(bbox)
        disp_w = GUARD_DRAW_WIDTH
        disp_h = disp_w * src.get_height() // src.get_width()
        img = pygame.transform.scale(src, (disp_w, disp_h))
        ratio = GUARD_RIGHT_BODY_CENTER_RATIO if guard["dir"] == 1 else GUARD_LEFT_BODY_CENTER_RATIO
        state.screen.blit(img, (rect.centerx - int(disp_w * ratio), rect.bottom - disp_h))
    else:
        pygame.draw.rect(state.screen, (35, 50, 80), rect)
        pygame.draw.rect(state.screen, BLACK, rect, 2)


def draw_board_menu():
    draw_corridor()
    draw_overlay(120)

    box = pygame.Rect(300, 180, 400, 300)
    pygame.draw.rect(state.screen, WHITE, box, border_radius=10)
    pygame.draw.rect(state.screen, BLACK, box, 4, border_radius=10)
    draw_text("엘리베이터", 500, 220, state.font_big, BLACK, center=True)
    draw_text("이동할 층을 선택하세요", 500, 270, state.font_mid, DARK_GRAY, center=True)
    draw_text("1 : 1층", 500, 325, state.font_mid, BLACK, center=True)
    draw_text("2 : 2층", 500, 365, state.font_mid, BLACK, center=True)
    draw_text("3 : 3층", 500, 405, state.font_mid, BLACK, center=True)
    draw_text("ESC : 닫기", 500, 450, state.font_small, RED, center=True)


def draw_caught_screen():
    if state.current_room is None:
        draw_corridor()
    else:
        draw_room()

    draw_overlay(155)

    panel = pygame.Rect(115, 165, 770, 320)
    pygame.draw.rect(state.screen, WHITE, panel, border_radius=14)
    pygame.draw.rect(state.screen, RED, panel, 6, border_radius=14)
    draw_text("!", 500, 235, state.font_huge, RED, center=True)
    draw_text("들켰습니다!", 500, 315, state.font_huge, RED, center=True)
    draw_text(state.caught_reason, 500, 380, state.font_reason, BLACK, center=True)
    draw_text("R 키를 누르면 처음부터 다시 시작합니다.", 500, 435, state.font_mid, DARK_GRAY, center=True)


def draw_cleared_screen():
    draw_room()
    draw_overlay(150)
    draw_text("A+ GAME CLEAR!", 500, 325, state.font_huge, YELLOW, center=True)


def draw_wrapped_text(text, x, y, font, color, max_width):
    lines = []
    current = ""
    for ch in text:
        test = current + ch
        if font.size(test)[0] > max_width:
            if current:
                lines.append(current)
            current = ch
        else:
            current = test
    if current:
        lines.append(current)

    line_h = font.get_linesize()
    for i, line in enumerate(lines):
        surf = font.render(line, True, color)
        state.screen.blit(surf, (x, y + i * line_h))


def draw_professor_dialog():
    draw_room()
    box_h = 200
    box_y = SCREEN_HEIGHT - box_h
    padding = 24

    overlay = pygame.Surface((SCREEN_WIDTH, box_h), pygame.SRCALPHA)
    overlay.fill((20, 20, 20, 210))
    state.screen.blit(overlay, (0, box_y))
    pygame.draw.line(state.screen, (180, 160, 100), (0, box_y), (SCREEN_WIDTH, box_y), 2)

    name_surf = state.font_mid.render("교수님", True, (255, 220, 100))
    state.screen.blit(name_surf, (padding, box_y + padding - 4))
    draw_wrapped_text(state.dialog_text, padding, box_y + padding + 30,
                      state.font_small, WHITE, SCREEN_WIDTH - padding * 2)

    hint_surf = state.font_tiny.render("[ SPACE ] 계속", True, (160, 160, 160))
    state.screen.blit(hint_surf, (SCREEN_WIDTH - hint_surf.get_width() - padding,
                                  SCREEN_HEIGHT - hint_surf.get_height() - 10))


def draw_game():
    if state.game_state == "board_menu":
        draw_board_menu()
    elif state.game_state == "caught":
        draw_caught_screen()
    elif state.game_state == "caught_animation":
        draw_room()
    elif state.game_state == "cleared":
        draw_cleared_screen()
    elif state.game_state == "professor_dialog":
        draw_professor_dialog()
    elif state.current_room is None:
        draw_corridor()
    else:
        draw_room()
