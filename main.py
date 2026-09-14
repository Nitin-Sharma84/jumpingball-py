# main.py
# STEP 1 of the project: a fully working, playable game with NO login/DB yet.
# Screens: Main Menu -> Ball Select -> Difficulty Select -> Gameplay -> Game Over
# High score is saved to a simple text file for now (data/highscore.txt).
# Login, SQLite, statistics, leaderboard will be added in Step 2.

import sound
import database as db
import auth
import screens
import gc
import pygame
import os
from config import WIDTH, HEIGHT, FPS, BALL_SKINS, WHITE, BLACK, SKY_BLUE, YELLOW, RED, GREEN,GRAY,BROWN
from game import run_gameplay, draw_text
import os
import assets_loader
import ui_helpers
import paths


gc.disable()

def draw_button(screen, rect, text, base_color, text_color=BLACK, text_size=28):
    pygame.draw.rect(screen, base_color, rect, border_radius=12)
    pygame.draw.rect(screen, BLACK, rect, 2, border_radius=12)
    draw_text(screen, text, text_size, text_color, rect.centerx, rect.centery)


def main_menu(screen, clock, username, high_score):
    buttons = [
        ("play", "Play Game", GREEN),
        ("leaderboard", "Leaderboard", YELLOW),
        ("statistics", "Statistics", YELLOW),
        ("history", "Game History", YELLOW),
        ("logout", "Logout", GRAY),
        ("delete_account", "Delete Account", RED),
        ("exit", "Exit", RED),
    ]
    sound_toggle_rect = pygame.Rect(WIDTH - 130, 15, 110, 35)
    button_w, button_h = 260, 42
    gap = 12
    start_y = 175
    rects = {}
    y = start_y
    for key, label, color in buttons:
        rects[key] = pygame.Rect(WIDTH // 2 - button_w // 2, y, button_w, button_h)
        y += button_h + gap
    panel_rect = pygame.Rect(WIDTH // 2 - 200, 20, 400, y + 20)

    while True:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "exit"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for key, rect in rects.items():
                    if rect.collidepoint(event.pos):
                        return key
                if sound_toggle_rect.collidepoint(event.pos):
                    sound.toggle_mute()

        ui_helpers.draw_screen_background(screen)
        ui_helpers.draw_panel(screen, panel_rect)
        draw_text(screen, "JUMPING BALL", 60, BROWN, WIDTH // 2, 60)
        draw_text(screen, f"Ready for the challenge, {username}?", 25, WHITE, WIDTH // 2, 110)
        draw_text(screen, f"High Score: {high_score}", 23, WHITE, WIDTH // 2, 135)

        for key, label, color in buttons:
            draw_button(screen, rects[key], label, color, WHITE if color != YELLOW else BLACK, text_size=22)

        label = "Sound: OFF" if sound.is_muted() else "Sound: ON"
        pygame.draw.rect(screen, GRAY, sound_toggle_rect, border_radius=8)
        draw_text(screen, label, 16, WHITE, *sound_toggle_rect.center)
        pygame.display.flip()


def ball_select_screen(screen, clock):
    selected = 0
    box_w, box_h = 140, 140
    gap = 30
    total_w = len(BALL_SKINS) * box_w + (len(BALL_SKINS) - 1) * gap
    start_x = WIDTH // 2 - total_w // 2
    boxes = []
    for i in range(len(BALL_SKINS)):
        rect = pygame.Rect(start_x + i * (box_w + gap), 220, box_w, box_h)
        boxes.append(rect)

    # Load thumbnail images ONCE here, not every frame
    thumbnails = []
    for skin in BALL_SKINS:
        name, color, image_filename = skin if len(skin) == 3 else (skin[0], skin[1], None)
        img = None
        if image_filename:
            img = assets_loader.load_image(
                paths.resource_path(os.path.join("assets/balls", image_filename)), (80, 80)
            )
        thumbnails.append(img)

    select_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT - 100, 200, 50)
    panel_rect = pygame.Rect(start_x - 40, 40, total_w + 80, 420)

    while True:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for i, rect in enumerate(boxes):
                    if rect.collidepoint(event.pos):
                        selected = i
                if select_rect.collidepoint(event.pos):
                    return BALL_SKINS[selected]

        ui_helpers.draw_screen_background(screen)
        ui_helpers.draw_panel(screen, panel_rect)
        draw_text(screen, "SELECT YOUR BALL", 42, WHITE, WIDTH // 2, 100)

        for i, rect in enumerate(boxes):
            skin = BALL_SKINS[i]
            name, color = skin[0], skin[1]
            pygame.draw.rect(screen, WHITE, rect, border_radius=14)
            border_color = YELLOW if i == selected else BLACK
            border_width = 5 if i == selected else 2
            pygame.draw.rect(screen, border_color, rect, border_width, border_radius=14)

            if thumbnails[i]:
                img_rect = thumbnails[i].get_rect(center=(rect.centerx, rect.centery - 10))
                screen.blit(thumbnails[i], img_rect)
            else:
                pygame.draw.circle(screen, color, (rect.centerx, rect.centery - 10), 40)

            draw_text(screen, name, 16, BLACK, rect.centerx, rect.bottom - 15)

        draw_button(screen, select_rect, "Select", GREEN, WHITE)
        pygame.display.flip()


def difficulty_select_screen(screen, clock):
    easy_rect = pygame.Rect(WIDTH // 2 - 110, 220, 220, 55)
    medium_rect = pygame.Rect(WIDTH // 2 - 110, 290, 220, 55)
    hard_rect = pygame.Rect(WIDTH // 2 - 110, 360, 220, 55)
    panel_rect = pygame.Rect(WIDTH // 2 - 180, 130, 360, 320)

    while True:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if easy_rect.collidepoint(event.pos):
                    return "Easy"
                if medium_rect.collidepoint(event.pos):
                    return "Medium"
                if hard_rect.collidepoint(event.pos):
                    return "Hard"

        ui_helpers.draw_screen_background(screen)
        ui_helpers.draw_panel(screen, panel_rect)
        draw_text(screen, "SELECT DIFFICULTY", 42, WHITE, WIDTH // 2, 165)
        draw_button(screen, easy_rect, "Easy", GREEN, WHITE)
        draw_button(screen, medium_rect, "Medium", YELLOW, BLACK)
        draw_button(screen, hard_rect, "Hard", RED, WHITE)
        pygame.display.flip()


def game_over_screen(screen, clock, score, high_score):
    retry_rect = pygame.Rect(WIDTH // 2 - 120, 320, 240, 55)
    menu_rect = pygame.Rect(WIDTH // 2 - 120, 390, 240, 55)
    panel_rect = pygame.Rect(WIDTH // 2 - 200, 90, 400, 380)

    while True:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "exit"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if retry_rect.collidepoint(event.pos):
                    return "retry"
                if menu_rect.collidepoint(event.pos):
                    return "menu"

        ui_helpers.draw_screen_background(screen)
        ui_helpers.draw_panel(screen, panel_rect)
        draw_text(screen, "GAME OVER", 55, RED, WIDTH // 2, 150)
        draw_text(screen, f"Final Score: {score}", 30, WHITE, WIDTH // 2, 220)
        draw_text(screen, f"High Score: {high_score}", 26, WHITE, WIDTH // 2, 260)
        draw_button(screen, retry_rect, "Retry", GREEN, WHITE)
        draw_button(screen, menu_rect, "Main Menu", YELLOW, BLACK)
        pygame.display.flip()


def main():
    pygame.init()
    db.init_db()
    sound.init_sound()
    sound.play_music()

    try:
        icon_surface = pygame.image.load(paths.resource_path("assets/icon/window_icon.png"))
        pygame.display.set_icon(icon_surface)
    except pygame.error:
        pass

    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SCALED, vsync=1)
    pygame.display.set_caption("Jumping Ball")
    clock = pygame.time.Clock()

    state = "auth"
    user_id = None
    username = None
    ball_choice = BALL_SKINS[0]
    difficulty = "Easy"
    last_score = 0

    while True:
        if state == "auth":
            result = auth.login_register_screen(screen, clock)
            if result is None:
                break
            user_id, username = result
            state = "menu"

        elif state == "menu":
            high_score = db.get_high_score(user_id)
            choice = main_menu(screen, clock, username, high_score)
            if choice == "exit":
                break
            elif choice == "logout":
                user_id, username = None, None
                state = "auth"
            elif choice == "delete_account":
                state = "delete_account"
            else:
                state = choice  # "play" / "leaderboard" / "statistics" / "history"

        elif state == "play":
            state = "ball_select"

        elif state == "ball_select":
            ball_choice = ball_select_screen(screen, clock)
            if ball_choice is None:
                break
            state = "difficulty_select"

        elif state == "difficulty_select":
            difficulty = difficulty_select_screen(screen, clock)
            if difficulty is None:
                break
            state = "gameplay"

        elif state == "gameplay":
            high_score = db.get_high_score(user_id)
            result = run_gameplay(screen, clock, difficulty, ball_choice, high_score)
            sound.play_music()
            if result.get("quit_game"):
                break
            last_score = result["score"]
            db.save_game(user_id, last_score, difficulty)
            if result.get("quit_to_menu"):
                state = "menu"
            else:
                state = "game_over"

        elif state == "game_over":
            high_score = db.get_high_score(user_id)
            choice = game_over_screen(screen, clock, last_score, high_score)
            if choice == "exit":
                break
            elif choice == "retry":
                state = "difficulty_select"
            else:
                state = "menu"

        elif state == "leaderboard":
            screens.leaderboard_screen(screen, clock)
            state = "menu"

        elif state == "statistics":
            screens.statistics_screen(screen, clock, user_id, username)
            state = "menu"

        elif state == "history":
            screens.history_screen(screen, clock, user_id)
            state = "menu"

        elif state == "delete_account":
            result = screens.delete_account_screen(screen, clock, user_id)
            if result == "deleted":
                user_id, username = None, None
                state = "auth"
            else:
                state = "menu"

    pygame.quit()


if __name__ == "__main__":
    main()