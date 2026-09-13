# assets_loader.py
# Loads images safely - if a file is missing or broken, returns None instead
# of crashing, so the game can fall back to plain shapes for that item.
# Also caches results so the same image/size is never loaded or rescaled
# more than once (important for performance - rescaling every frame is slow).

import os
import pygame

_cache = {}


def load_image(path, size=None):
    """Returns a pygame.Surface, or None if the file is missing/broken.
    `size` is an optional (width, height) to scale to."""
    key = (path, size)
    if key in _cache:
        return _cache[key]

    image = None
    if os.path.exists(path):
        try:
            image = pygame.image.load(path).convert_alpha()
            if size:
                image = pygame.transform.smoothscale(image, size)
        except pygame.error as e:
            print(f"Could not load image '{path}', using fallback shape instead:", e)
            image = None

    _cache[key] = image
    return image
