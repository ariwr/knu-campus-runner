import sys
import pygame

import audio
import game_state as state
import mechanics
import render
from assets_loader import load_assets as load_game_assets
from config import FPS, SCREEN_HEIGHT, SCREEN_WIDTH


def get_font(size):
    font_names = ["malgungothic", "applegothic", "nanumgothic", None]
    for name in font_names:
        try:
            return pygame.font.SysFont(name, size)
        except Exception:
            pass
    return pygame.font.Font(None, size)


def make_fonts():
    return {
        "tiny": get_font(16),
        "small": get_font(18),
        "mid": get_font(24),
        "reason": get_font(30),
        "big": get_font(42),
        "huge": get_font(72),
    }


def handle_keydown(event):
    if event.key == pygame.K_r:
        mechanics.reset_game()
        return

    if state.game_state == "board_menu":
        if event.key == pygame.K_ESCAPE:
            mechanics.close_board_menu()
        elif event.key == pygame.K_1:
            mechanics.change_floor(1)
        elif event.key == pygame.K_2:
            mechanics.change_floor(2)
        elif event.key == pygame.K_3:
            mechanics.change_floor(3)
        return

    if state.game_state == "professor_dialog":
        if event.key == pygame.K_SPACE:
            if state.dialog_result == "cleared":
                state.game_state = "cleared"
                audio.play_gameclear_music()
            else:
                state.game_state = "playing"
        return

    if state.game_state == "playing" and event.key == pygame.K_SPACE:
        mechanics.handle_space_action()


def update_game():
    if state.game_state == "playing":
        keys = pygame.key.get_pressed()
        if state.current_room is None:
            mechanics.move_player(keys, pygame.Rect(50, 420, 900, 150))
            mechanics.update_corridor_guard()
        else:
            walls = mechanics.room_collision_walls(state.current_room)
            allowed = pygame.Rect(90, 100, 820, 480)
            player_moved = mechanics.move_player(keys, allowed, walls)
            mechanics.update_room_gimmick(player_moved)
            mechanics.check_item_collision()

    elif state.game_state == "caught_animation":
        state.caught_animation_timer -= 1
        if state.caught_animation_timer <= 0:
            state.game_state = "caught"

    if state.message_timer > 0:
        state.message_timer -= 1
    else:
        state.message_text = ""


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("A+ Escape: IT4호관 탈출")
    clock = pygame.time.Clock()

    assets = load_game_assets()
    state.setup_runtime(screen, assets, make_fonts())
    mechanics.reset_game(show_message=False)

    running = True
    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                handle_keydown(event)

        update_game()
        render.draw_game()
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
