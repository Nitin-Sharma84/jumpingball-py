# sound.py
# Simple sound manager. If a sound/music file is missing or fails to load,
# the game keeps running silently instead of crashing - so you can add
# real audio files later without touching any other code.

import os
import pygame
import paths

SOUND_DIR = "assets/sounds"

_sounds = {}
_music_loaded = False
_enabled = True
_muted = False

SOUND_FILES = {
    "jump": "jump.wav",
    "collision": "collision.wav",
    "score": "score.wav",
    "game_over": "game_over.wav",
    "button": "button_click.wav",
}
MUSIC_FILE = "background_music.mp3"


def init_sound():
    """Call once, right after pygame.init()."""
    global _enabled
    try:
        pygame.mixer.init()
    except pygame.error as e:
        print("Sound system unavailable, continuing without audio:", e)
        _enabled = False
        return

    for name, filename in SOUND_FILES.items():
        _sounds[name] = _try_load_sound(paths.resource_path(os.path.join(SOUND_DIR, filename)))

    _try_load_music(paths.resource_path(os.path.join(SOUND_DIR, MUSIC_FILE)))


def _try_load_sound(path):
    if not os.path.exists(path):
        return None
    try:
        return pygame.mixer.Sound(path)
    except pygame.error as e:
        print(f"Could not load sound '{path}', continuing without it:", e)
        return None


def _try_load_music(path):
    global _music_loaded
    if not os.path.exists(path):
        return
    try:
        pygame.mixer.music.load(path)
        _music_loaded = True
    except pygame.error as e:
        print(f"Could not load background music '{path}', continuing without it:", e)


def play(name, volume=1.0):
    """Play a one-shot sound effect by name (e.g. 'jump', 'collision', 'score')."""
    if not _enabled or _muted:
        return
    sound = _sounds.get(name)
    if sound:
        sound.set_volume(volume)
        sound.play()


def play_music(volume=0.4):
    if not _enabled or not _music_loaded or _muted:
        return
    try:
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(-1)  # loop forever
    except pygame.error:
        pass


def stop_music():
    if not _enabled:
        return
    try:
        pygame.mixer.music.stop()
    except pygame.error:
        pass


def toggle_mute():
    """Flip mute on/off. Stops music immediately when muting, resumes it when unmuting."""
    global _muted
    _muted = not _muted
    if _muted:
        stop_music()
    else:
        play_music()
    return _muted


def is_muted():
    return _muted