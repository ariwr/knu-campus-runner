import pygame


BGM_BACKGROUND = "assets/bgm/background.mp3"
BGM_GAMECLEAR = "assets/bgm/gameclear.mp3"

music_track = None
music_enabled = True


def play_music(path, loops=-1, volume=0.45):
    global music_track, music_enabled

    if not music_enabled or music_track == path:
        return

    try:
        pygame.mixer.music.load(path)
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(loops)
        music_track = path
    except pygame.error:
        music_enabled = False
        music_track = None


def play_background_music():
    play_music(BGM_BACKGROUND, loops=-1, volume=0.42)


def play_gameclear_music():
    play_music(BGM_GAMECLEAR, loops=0, volume=0.65)
