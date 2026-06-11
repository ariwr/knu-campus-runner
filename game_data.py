import random

import pygame

from config import GREEN, ORANGE, PURPLE, YELLOW


def make_item(name, x, y, symbol, color):
    return {
        "name": name,
        "rect": pygame.Rect(x, y, 34, 34),
        "symbol": symbol,
        "color": color,
        "collected": False,
    }


def make_student(x, y, look_interval=180, look_duration=65, sight_rect=None,
                 normal_image_key="boy_studyroom", look_image_key="boy_studyroom_look",
                 student_type="studyroom"):
    if sight_rect is None:
        sight_rect = pygame.Rect(x - 45, y + 35, 130, 120)
    return {
        "rect": pygame.Rect(x, y, 44, 60),
        "state": "studying",
        "timer": 0,
        "look_interval": look_interval,
        "look_duration": look_duration,
        "sight_rect": sight_rect,
        "normal_image_key": normal_image_key,
        "look_image_key": look_image_key,
        "student_type": student_type,
    }


def make_study_student(x, y, gender="boy", look_duration=70):
    prefix = "boy" if gender == "boy" else "girl"
    return make_student(
        x, y, look_duration=look_duration,
        normal_image_key=f"{prefix}_studyroom",
        look_image_key=f"{prefix}_studyroom_look",
        student_type="studyroom",
    )


def make_classroom_student(x, y, gender="boy"):
    prefix = "boy" if gender == "boy" else "girl"
    return make_student(
        x, y, look_duration=60,
        normal_image_key=f"{prefix}_classroom",
        look_image_key=f"{prefix}_classroom_look",
        student_type="classroom",
    )


def make_classroom_students():
    return [
        # 앞줄
        make_classroom_student(280, 365, "boy"),
        make_classroom_student(620, 365, "boy"),
        # 뒷줄
        make_classroom_student(240, 465, "girl"),
        make_classroom_student(410, 465, "girl"),
        make_classroom_student(590, 465, "boy"),
        make_classroom_student(760, 465, "girl"),
    ]


def make_room(room_id, name, door_rect, kind="empty", items=None, students=None, professor=None, desks=None, entry_rect=None):
    return {
        "id": room_id,
        "name": name,
        "door_rect": door_rect,
        "entry_rect": entry_rect if entry_rect is not None else door_rect,
        "kind": kind,  # empty, students, professor_trap, goal_professor
        "items": items if items is not None else [],
        "students": students if students is not None else [],
        "professor": professor,
        "desks": desks if desks is not None else [],
        "look_timer": 0,
        "next_look_time": random.randint(120, 240),
        "active_looking_student": None,
    }


def make_classroom_professor():
    return {
        "rect": pygame.Rect(455, 245, 60, 80),
        "state": "teaching",
        "normal_image_key": "professor_classroom",
        "alert_image_key": "professor_classroom_angry",
        "draw_width": 95,
        "sprite_offset_x": 0,
        "sprite_offset_y": 0,
        "sight_offset_x": 0.0,
        "sight_min_offset_x": -170,
        "sight_max_offset_x": 170,
        "sight_speed": 0.8,
        "sight_dir": 1,
        "sight_length": 145,
        "sight_half_width": 115,
    }


def make_guard(x, y, min_x, max_x, speed=2.0):
    return {
        "rect": pygame.Rect(x, y, 44, 70),
        "min_x": min_x,
        "max_x": max_x,
        "speed": speed,
        "dir": 1,
    }

# ---------------------------------------------------------
# 방 내부 장애물/책상 배치
# ---------------------------------------------------------
def normal_classroom_desks():
    return [
        pygame.Rect(210, 305, 95, 28), pygame.Rect(360, 305, 95, 28), pygame.Rect(510, 305, 95, 28), pygame.Rect(660, 305, 95, 28),
        pygame.Rect(210, 390, 95, 28), pygame.Rect(360, 390, 95, 28), pygame.Rect(510, 390, 95, 28), pygame.Rect(660, 390, 95, 28),
    ]


def auditorium_desks():
    desks = []
    for y in [260, 335, 410, 485]:
        desks.append(pygame.Rect(130, y, 210, 24))
        desks.append(pygame.Rect(390, y, 210, 24))
        desks.append(pygame.Rect(650, y, 210, 24))
    return desks

# ---------------------------------------------------------
# 층별 맵 데이터
# ---------------------------------------------------------
# 엘리베이터는 층 이동 메뉴 역할을 한다. 계단은 사용하지 않는다.
floors = {
    1: {
        "name": "1층",
        "start": (80, 500),
        "board_rect": pygame.Rect(430, 300, 140, 80),
        "elevator_rect": pygame.Rect(862, 250, 96, 180),  # 장식용
        "rooms": [],
        "guards": [],  # 1층에는 경비가 없다.
    },
    2: {
        "name": "2층",
        "start": (80, 500),
        "board_rect": pygame.Rect(430, 300, 140, 80),
        "elevator_rect": pygame.Rect(862, 250, 96, 180),
        "rooms": [],
        "guards": [make_guard(160, 490, 120, 760, 2.3)],
    },
    3: {
        "name": "3층",
        "start": (80, 500),
        "board_rect": pygame.Rect(430, 300, 140, 80),
        "elevator_rect": pygame.Rect(862, 250, 96, 180),
        "rooms": [],
        "guards": [make_guard(650, 490, 180, 760, 2.0)],
    },
}

# 복도에 표시될 방문 좌표
# 각 층마다 같은 구조를 쓰되, 방 번호와 기믹을 다르게 둔다.
def make_entry_zone(center_x, y=410, width=90, height=80):
    """배경 이미지 속 문 중심 x좌표를 기준으로 플레이어 입장 가능 바닥 영역을 만든다."""
    return pygame.Rect(center_x - width // 2, y, width, height)


def add_corridor_rooms():
    door_y = 340
    door_w = 44
    door_h = 28
    dc = [73, 188, 304, 559, 670, 784]

    def dr(i):
        return pygame.Rect(dc[i] - door_w // 2, door_y, door_w, door_h)

    # 1층: 101~106
    floors[1]["rooms"] = [
        make_room("101", "101호 수업 중 강의실", dr(0), "professor_trap",
                  items=[make_item("변수 노트", 170, 270, "x", GREEN)],
                  students=make_classroom_students(),
                  professor=make_classroom_professor(),
                  desks=normal_classroom_desks(), entry_rect=make_entry_zone(dc[0])),
        make_room("102", "102호 자습실", dr(1), "students",
                  students=[
                      make_study_student(280, 345, "girl"),
                      make_study_student(420, 345, "boy"),
                      make_study_student(560, 345, "girl"),
                      make_study_student(700, 345, "boy"),
                  ],
                  desks=normal_classroom_desks(), entry_rect=make_entry_zone(dc[1])),
        make_room("103", "103호 자습실", dr(2), "students",
                  items=[make_item("조건문 카드", 805, 445, "if", YELLOW)],
                  students=[
                      make_study_student(280, 345, "boy"),
                      make_study_student(420, 345, "girl"),
                      make_study_student(560, 345, "boy"),
                      make_study_student(700, 345, "girl"),
                  ],
                  desks=normal_classroom_desks(), entry_rect=make_entry_zone(dc[2])),
        make_room("104", "104호 빈 강의실", dr(3), "empty",
                  desks=normal_classroom_desks(), entry_rect=make_entry_zone(dc[3])),
        make_room("105", "105호 수업 중 강의실", dr(4), "professor_trap",
                  students=make_classroom_students(),
                  professor=make_classroom_professor(),
                  desks=normal_classroom_desks(), entry_rect=make_entry_zone(dc[4])),
        make_room("106", "106호 수업 중 강의실", dr(5), "professor_trap",
                  students=make_classroom_students(),
                  professor=make_classroom_professor(),
                  desks=normal_classroom_desks(), entry_rect=make_entry_zone(dc[5])),
    ]

    # 2층: 201~206
    floors[2]["rooms"] = [
        make_room("201", "201호 수업 중 강의실", dr(0), "professor_trap",
                  students=make_classroom_students(),
                  professor=make_classroom_professor(),
                  desks=normal_classroom_desks(), entry_rect=make_entry_zone(dc[0])),
        make_room("202", "202호 자습실", dr(1), "students",
                  items=[make_item("반복문 배지", 176, 445, "for", ORANGE)],
                  students=[
                      make_study_student(260, 345, "girl"),
                      make_study_student(400, 345, "boy"),
                      make_study_student(540, 345, "girl"),
                      make_study_student(680, 345, "boy"),
                  ],
                  desks=normal_classroom_desks(), entry_rect=make_entry_zone(dc[1])),
        make_room("203", "203호 수업 중 강의실", dr(2), "professor_trap",
                  students=make_classroom_students(),
                  professor=make_classroom_professor(),
                  desks=normal_classroom_desks(), entry_rect=make_entry_zone(dc[2])),
        make_room("204", "204호 빈 강의실", dr(3), "empty",
                  items=[make_item("함수 열쇠", 483, 300, "def", PURPLE)],
                  desks=normal_classroom_desks(), entry_rect=make_entry_zone(dc[3])),
        make_room("205", "205호 빈 강의실", dr(4), "empty",
                  desks=normal_classroom_desks(), entry_rect=make_entry_zone(dc[4])),
        make_room("206", "206호 빈 강의실", dr(5), "empty",
                  desks=normal_classroom_desks(), entry_rect=make_entry_zone(dc[5])),
    ]

    goal_professor = {
        "rect": pygame.Rect(475, 135, 48, 58),
        "dialog_ready": "그래, 자네는 모든 과제를 훌륭히 수행했구만. 자네는 A+일세!",
        "dialog_not_ready": "아직 모든 과제를 수행하지 않았네. Python 개념을 더 모아오게!",
    }
    # 3층: 301, 302, 교수실 (아이템은 302에만)
    floors[3]["rooms"] = [
        make_room("301", "301호 빈 강의실", pygame.Rect(89, door_y, 44, door_h), "empty",
                  desks=normal_classroom_desks(), entry_rect=make_entry_zone(111)),
        make_room("302", "302호 자습실", pygame.Rect(211, door_y, 44, door_h), "students",
                  items=[make_item("딕셔너리 지도", 805, 520, "{}", YELLOW)],
                  students=[
                      make_study_student(330, 345, "boy"),
                      make_study_student(500, 345, "girl"),
                      make_study_student(670, 345, "boy"),
                  ],
                  desks=normal_classroom_desks(), entry_rect=make_entry_zone(233)),
        make_room("교수실", "교수실", pygame.Rect(610, door_y, 140, door_h), "goal_professor",
                  professor=goal_professor, desks=auditorium_desks(),
                  entry_rect=make_entry_zone(680, width=170)),
    ]


add_corridor_rooms()
