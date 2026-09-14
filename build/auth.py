# auth.py
# Login / Register screen. Returns (user_id, username) on success, or None if the
# window was closed. Talks to database.py only through create_user()/verify_login().

import pygame
from config import WIDTH, HEIGHT, WHITE, BLACK, GREEN, YELLOW, RED, GRAY
from game import get_font
import ui_helpers
import database as db

FPS = 60


def draw_field_text(screen, text, size, color, x, center_y):
    font = get_font(size)
    surf = font.render(text, True, color)
    rect = surf.get_rect(midleft=(x, center_y))
    screen.blit(surf, rect)


def draw_center_text(screen, text, size, color, x, y):
    font = get_font(size)
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=(x, y))
    screen.blit(surf, rect)


def login_register_screen(screen, clock):
    mode = "login"
    username_text = ""
    password_text = ""
    active_field = None
    show_password = False
    message = ""
    message_color = RED

    panel_rect = pygame.Rect(WIDTH // 2 - 230, 40, 460, 460)

    username_rect = pygame.Rect(WIDTH // 2 - 150, 220, 300, 45)
    password_rect = pygame.Rect(WIDTH // 2 - 150, 285, 300, 45)
    show_pw_rect = pygame.Rect(WIDTH // 2 + 160, 285, 70, 45)
    submit_rect = pygame.Rect(WIDTH // 2 - 100, 350, 200, 50)
    toggle_rect = pygame.Rect(WIDTH // 2 - 150, 420, 300, 35)

    while True:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if username_rect.collidepoint(event.pos):
                    active_field = "username"
                elif password_rect.collidepoint(event.pos):
                    active_field = "password"
                elif show_pw_rect.collidepoint(event.pos):
                    show_password = not show_password
                elif submit_rect.collidepoint(event.pos):
                    message = ""
                    if mode == "login":
                        user_id = db.verify_login(username_text, password_text)
                        if user_id:
                            return (user_id, username_text.strip())
                        message = "Invalid username or password"
                        message_color = RED
                    else:
                        ok, result = db.create_user(username_text, password_text)
                        if ok:
                            mode = "login"
                            message = "Account created! Please login."
                            message_color = GREEN
                        else:
                            message = result
                            message_color = RED
                elif toggle_rect.collidepoint(event.pos):
                    mode = "register" if mode == "login" else "login"
                    message = ""

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    if active_field is None or active_field == "password":
                        active_field = "username"
                    else:
                        active_field = "password"
                elif event.key == pygame.K_BACKSPACE:
                    if active_field == "username":
                        username_text = username_text[:-1]
                    elif active_field == "password":
                        password_text = password_text[:-1]
                elif event.key == pygame.K_RETURN:
                    pygame.event.post(pygame.event.Event(
                        pygame.MOUSEBUTTONDOWN, pos=submit_rect.center, button=1
                    ))
                else:
                    ch = event.unicode
                    if ch and ch.isprintable():
                        if active_field == "username" and len(username_text) < 24:
                            username_text += ch
                        elif active_field == "password" and len(password_text) < 24:
                            password_text += ch

        # --- Draw ---
        ui_helpers.draw_screen_background(screen)
        ui_helpers.draw_panel(screen, panel_rect)

        draw_center_text(screen, "JUMPING BALL", 46, WHITE, WIDTH // 2, 110)
        draw_center_text(screen, "Login to Continue" if mode == "login" else "Create Account",
                          24, WHITE, WIDTH // 2, 160)

        cursor_visible = (pygame.time.get_ticks() // 500) % 2 == 0

        for rect, field_name, text, is_password in (
            (username_rect, "username", username_text, False),
            (password_rect, "password", password_text, True),
        ):
            pygame.draw.rect(screen, WHITE, rect, border_radius=8)
            is_active = active_field == field_name
            border_color = YELLOW if is_active else GRAY
            pygame.draw.rect(screen, border_color, rect, 3, border_radius=8)

            if is_password and not show_password:
                shown = "*" * len(text)
            else:
                shown = text

            if is_active:
                display_text = shown + ("|" if cursor_visible else "")
                color = BLACK
            elif shown:
                display_text = shown
                color = BLACK
            else:
                display_text = f"Enter {field_name}"
                color = GRAY

            draw_field_text(screen, display_text, 22, color, rect.x + 12, rect.centery)

        pygame.draw.rect(screen, GRAY, show_pw_rect, border_radius=8)
        draw_center_text(screen, "Hide" if show_password else "Show", 15, WHITE, *show_pw_rect.center)

        submit_label = "Login" if mode == "login" else "Create Account"
        pygame.draw.rect(screen, GREEN, submit_rect, border_radius=10)
        draw_center_text(screen, submit_label, 26, WHITE, *submit_rect.center)

        toggle_label = ("New here? Register" if mode == "login"
                         else "Already have an account? Login")
        draw_center_text(screen, toggle_label, 20, WHITE, WIDTH // 2, toggle_rect.centery)

        if message:
            draw_center_text(screen, message, 20, message_color, WIDTH // 2, 470)

        pygame.display.flip()