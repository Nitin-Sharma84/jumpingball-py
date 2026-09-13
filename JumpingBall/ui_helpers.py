# ui_helpers.py
# Shared visual helpers so every screen (menu, login, leaderboard, etc.)
# uses the same background image and a consistent "panel" look, instead of
# each screen having its own plain flat-color fill.

import pygame
import assets_loader
import paths
from config import WIDTH, HEIGHT, SKY_BLUE, BLACK

BG_IMAGE_PATH = "assets/backgrounds/background.png"


def draw_screen_background(screen):
    """Use this instead of screen.fill(SKY_BLUE) at the top of every screen's draw code."""
    bg = assets_loader.load_image(paths.resource_path(BG_IMAGE_PATH), (WIDTH, HEIGHT))
    if bg:
        screen.blit(bg, (0, 0))
    else:
        screen.fill(SKY_BLUE)


def draw_panel(screen, rect, alpha=190, color=(20, 20, 30), border_radius=18):
    """A semi-transparent rounded panel to place UI content on top of,
    so text/buttons stay readable against a busy background image."""
    panel = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(panel, (*color, alpha), panel.get_rect(), border_radius=border_radius)
    screen.blit(panel, rect.topleft)