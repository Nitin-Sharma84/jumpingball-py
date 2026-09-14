# screens.py
# Statistics, Leaderboard, Game History, Delete Account screens.
# Each function returns "back" when the user wants to return to the main menu.

import pygame
from config import WIDTH, HEIGHT, WHITE, BLACK, GREEN, YELLOW, RED, GRAY
import ui_helpers
from game import draw_text
import database as db

FPS = 60


def _back_button(screen):
    rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT - 80, 200, 50)
    pygame.draw.rect(screen, YELLOW, rect, border_radius=10)
    draw_text(screen, "Back", 26, BLACK, *rect.center)
    return rect


def statistics_screen(screen, clock, user_id, username):
    stats = db.get_stats(user_id)
    panel_rect = pygame.Rect(WIDTH // 2 - 250, 40, 500, 470)

    while True:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "back"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if back_rect.collidepoint(event.pos):
                    return "back"

        ui_helpers.draw_screen_background(screen)
        ui_helpers.draw_panel(screen, panel_rect)
        draw_text(screen, "PLAYER STATISTICS", 40, WHITE, WIDTH // 2, 90)
        draw_text(screen, f"Player: {username}", 20, WHITE, WIDTH // 2, 130)

        lines = [
            f"Games Played: {stats['games_played']}",
            f"Best Score: {stats['best_score']}",
            f"Average Score: {stats['avg_score']}",
            f"Easy Best: {stats['best_easy']}",
            f"Medium Best: {stats['best_medium']}",
            f"Hard Best: {stats['best_hard']}",
        ]
        y = 195
        for line in lines:
            draw_text(screen, line, 24, WHITE, WIDTH // 2, y)
            y += 45

        back_rect = _back_button(screen)
        pygame.display.flip()


def leaderboard_screen(screen, clock):
    current_filter = None  # None = All
    rows = db.get_leaderboard(current_filter, limit=10)
    panel_rect = pygame.Rect(WIDTH // 2 - 320, 30, 640, 500)

    filter_rects = {
        "All": pygame.Rect(WIDTH // 2 - 300, 130, 140, 40),
        "Easy": pygame.Rect(WIDTH // 2 - 150, 130, 140, 40),
        "Medium": pygame.Rect(WIDTH // 2 + 0, 130, 140, 40),
        "Hard": pygame.Rect(WIDTH // 2 + 150, 130, 140, 40),
    }

    while True:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "back"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if back_rect.collidepoint(event.pos):
                    return "back"
                for label, rect in filter_rects.items():
                    if rect.collidepoint(event.pos):
                        current_filter = None if label == "All" else label
                        rows = db.get_leaderboard(current_filter, limit=10)

        ui_helpers.draw_screen_background(screen)
        ui_helpers.draw_panel(screen, panel_rect)
        draw_text(screen, "LEADERBOARD", 40, WHITE, WIDTH // 2, 70)
        draw_text(screen, "Top 10 Players", 18, WHITE, WIDTH // 2, 100)

        for label, rect in filter_rects.items():
            active = (current_filter == label) or (current_filter is None and label == "All")
            color = GREEN if active else WHITE
            pygame.draw.rect(screen, color, rect, border_radius=8)
            pygame.draw.rect(screen, BLACK, rect, 2, border_radius=8)
            draw_text(screen, label, 18, BLACK, *rect.center)

        draw_text(screen, "Rank", 18, WHITE, WIDTH // 2 - 280, 200, center=False)
        draw_text(screen, "Username", 18, WHITE, WIDTH // 2 - 180, 200, center=False)
        draw_text(screen, "Level", 18, WHITE, WIDTH // 2 + 60, 200, center=False)
        draw_text(screen, "Score", 18, WHITE, WIDTH // 2 + 200, 200, center=False)

        y = 240
        for i, (uname, diff, score) in enumerate(rows, start=1):
            draw_text(screen, str(i), 18, WHITE, WIDTH // 2 - 280, y, center=False)
            draw_text(screen, uname, 18, WHITE, WIDTH // 2 - 180, y, center=False)
            draw_text(screen, diff, 18, WHITE, WIDTH // 2 + 60, y, center=False)
            draw_text(screen, str(score), 18, WHITE, WIDTH // 2 + 200, y, center=False)
            y += 32

        if not rows:
            draw_text(screen, "No scores yet", 20, GRAY, WIDTH // 2, 280)

        back_rect = _back_button(screen)
        pygame.display.flip()


def history_screen(screen, clock, user_id):
    rows = db.get_history(user_id, limit=10)
    panel_rect = pygame.Rect(WIDTH // 2 - 320, 30, 640, 460)

    while True:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "back"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if back_rect.collidepoint(event.pos):
                    return "back"

        ui_helpers.draw_screen_background(screen)
        ui_helpers.draw_panel(screen, panel_rect)
        draw_text(screen, "GAME HISTORY", 40, WHITE, WIDTH // 2, 80)
        draw_text(screen, "Date/Time", 18, WHITE, WIDTH // 2 - 280, 140, center=False)
        draw_text(screen, "Difficulty", 18, WHITE, WIDTH // 2 - 40, 140, center=False)
        draw_text(screen, "Score", 18, WHITE, WIDTH // 2 + 180, 140, center=False)

        y = 180
        for played_at, diff, score in rows:
            draw_text(screen, played_at, 16, WHITE, WIDTH // 2 - 280, y, center=False)
            draw_text(screen, diff, 16, WHITE, WIDTH // 2 - 40, y, center=False)
            draw_text(screen, str(score), 16, WHITE, WIDTH // 2 + 180, y, center=False)
            y += 30

        if not rows:
            draw_text(screen, "No games played yet", 20, GRAY, WIDTH // 2, 220)

        back_rect = _back_button(screen)
        pygame.display.flip()


def delete_account_screen(screen, clock, user_id):
    """Returns 'deleted' if the account was deleted, or 'back' otherwise."""
    panel_rect = pygame.Rect(WIDTH // 2 - 270, 120, 540, 300)
    yes_rect = pygame.Rect(WIDTH // 2 - 220, 320, 200, 55)
    no_rect = pygame.Rect(WIDTH // 2 + 20, 320, 200, 55)

    while True:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "back"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if yes_rect.collidepoint(event.pos):
                    db.delete_user(user_id)
                    return "deleted"
                if no_rect.collidepoint(event.pos):
                    return "back"

        ui_helpers.draw_screen_background(screen)
        ui_helpers.draw_panel(screen, panel_rect)
        draw_text(screen, "DELETE ACCOUNT", 38, RED, WIDTH // 2, 180)
        draw_text(screen, "This will permanently delete your account", 20, WHITE, WIDTH // 2, 230)
        draw_text(screen, "and all your scores. This cannot be undone.", 20, WHITE, WIDTH // 2, 260)

        pygame.draw.rect(screen, RED, yes_rect, border_radius=10)
        draw_text(screen, "Yes, Delete", 24, WHITE, *yes_rect.center)
        pygame.draw.rect(screen, GREEN, no_rect, border_radius=10)
        draw_text(screen, "Cancel", 24, WHITE, *no_rect.center)

        pygame.display.flip()