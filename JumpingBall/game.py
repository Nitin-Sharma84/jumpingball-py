# game.py
# Core gameplay: Ball, Pipe, and the main play loop.

import pygame
import random
import os
import sound
import assets_loader
import paths
from config import (
    WIDTH, HEIGHT, GRAVITY, JUMP_STRENGTH, BALL_RADIUS, BALL_START_X,
    GROUND_HEIGHT, PIPE_WIDTH, DIFFICULTY_SETTINGS, STARTING_LIVES,
    WHITE, BLACK, SKY_BLUE, GREEN, DARK_GREEN, RED, YELLOW, GRAY
)

BALL_IMAGE_DIR = "assets/balls"
PIPE_IMAGE_PATH = "assets/pipes/pipe.png"
BG_IMAGE_PATH = "assets/backgrounds/background.png"
GROUND_IMAGE_PATH = "assets/backgrounds/ground.png"


class Ball:
    def __init__(self, color, image_filename=None):
        self.x = BALL_START_X
        self.y = HEIGHT // 2
        self.vel_y = 0
        self.radius = BALL_RADIUS
        self.color = color
        self.image = None
        if image_filename:
            path = paths.resource_path(os.path.join(BALL_IMAGE_DIR, image_filename))
            self.image = assets_loader.load_image(path, (self.radius * 2, self.radius * 2))

    def jump(self):
        self.vel_y = JUMP_STRENGTH

    def update(self):
        self.vel_y += GRAVITY
        self.y += self.vel_y

    def reset(self):
        self.y = HEIGHT // 2
        self.vel_y = 0

    def get_rect(self):
        return pygame.Rect(
            self.x - self.radius, self.y - self.radius,
            self.radius * 2, self.radius * 2
        )

    def draw(self, screen):
        if self.image:
            rect = self.image.get_rect(center=(int(self.x), int(self.y)))
            screen.blit(self.image, rect)
        else:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
            pygame.draw.circle(screen, BLACK, (int(self.x), int(self.y)), self.radius, 2)


class Pipe:
    # Shared raw pipe image for every pipe this session. Set once per
    # gameplay session via Pipe.set_pipe_image() - NOT reloaded per pipe.
    pipe_image = None

    @classmethod
    def set_pipe_image(cls, image):
        cls.pipe_image = image

    def __init__(self, x, gap_size, speed):
        self.x = x
        self.width = PIPE_WIDTH
        self.speed = speed
        self.gap_size = gap_size
        margin = 80
        playable_bottom = HEIGHT - GROUND_HEIGHT - margin
        self.gap_y = random.randint(margin + gap_size // 2, playable_bottom - gap_size // 2)
        self.passed = False
        self._top_rect = None
        self._bottom_rect = None
        self._recompute_rects()

        # Pre-scale the pipe image ONCE here, since a pipe's gap height never
        # changes after it's created (only its x position moves each frame).
        # Rescaling an image every single frame is expensive and was part of
        # the earlier jitter problem - so this only happens at creation time.
        self._top_img = None
        self._bottom_img = None
        if Pipe.pipe_image:
            top_h = self._top_rect.height
            bottom_h = self._bottom_rect.height
            if top_h > 0:
                scaled = pygame.transform.scale(Pipe.pipe_image, (self.width, top_h))
                self._top_img = pygame.transform.flip(scaled, False, True)  # flipped = top pipe
            if bottom_h > 0:
                self._bottom_img = pygame.transform.scale(Pipe.pipe_image, (self.width, bottom_h))

    def _recompute_rects(self):
        top_height = self.gap_y - self.gap_size // 2
        self._top_rect = pygame.Rect(self.x, 0, self.width, top_height)
        bottom_y = self.gap_y + self.gap_size // 2
        self._bottom_rect = pygame.Rect(self.x, bottom_y, self.width, HEIGHT - GROUND_HEIGHT - bottom_y)

    def update(self):
        self.x -= self.speed
        self._recompute_rects()

    def off_screen(self):
        return self.x + self.width < 0

    def top_rect(self):
        return self._top_rect

    def bottom_rect(self):
        return self._bottom_rect

    def draw(self, screen):
        if self._top_img:
            screen.blit(self._top_img, self._top_rect)
        else:
            pygame.draw.rect(screen, GREEN, self._top_rect)
            pygame.draw.rect(screen, DARK_GREEN, self._top_rect, 3)

        if self._bottom_img:
            screen.blit(self._bottom_img, self._bottom_rect)
        else:
            pygame.draw.rect(screen, GREEN, self._bottom_rect)
            pygame.draw.rect(screen, DARK_GREEN, self._bottom_rect, 3)


_FONT_CACHE = {}
GAME_FONT_PATH = "assets/fonts/game_font.ttf"


def get_font(size):
    if size not in _FONT_CACHE:
        try:
            font_path = paths.resource_path(GAME_FONT_PATH)
            if os.path.exists(font_path):
                _FONT_CACHE[size] = pygame.font.Font(font_path, size)
            else:
                _FONT_CACHE[size] = pygame.font.SysFont("arial", size, bold=True)
        except pygame.error:
            _FONT_CACHE[size] = pygame.font.SysFont("arial", size, bold=True)
    return _FONT_CACHE[size]


def draw_text(screen, text, size, color, x, y, center=True):
    font = get_font(size)
    surf = font.render(text, True, color)
    rect = surf.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    screen.blit(surf, rect)
    return rect


def draw_lives(screen, lives, max_lives):
    for i in range(max_lives):
        color = RED if i < lives else GRAY
        pygame.draw.circle(screen, color, (25 + i * 30, 25), 10)


def draw_pause_overlay(screen):
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(180)
    overlay.fill(BLACK)
    screen.blit(overlay, (0, 0))
    draw_text(screen, "GAME PAUSED", 48, WHITE, WIDTH // 2, HEIGHT // 2 - 60)
    resume_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2, 200, 50)
    quit_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 70, 200, 50)
    pygame.draw.rect(screen, YELLOW, resume_rect, border_radius=10)
    pygame.draw.rect(screen, RED, quit_rect, border_radius=10)
    draw_text(screen, "Resume", 28, BLACK, *resume_rect.center)
    draw_text(screen, "Quit to Menu", 26, WHITE, *quit_rect.center)
    return resume_rect, quit_rect


def run_gameplay(screen, clock, difficulty, ball_skin, high_score):
    """
    ball_skin: (name, color, image_filename_or_None)
    Runs one full play session until the player loses all lives or quits.
    Returns a dict: {"score": int, "quit_to_menu": bool, "quit_game": bool}
    """
    sound.stop_music()  # no background music during actual gameplay

    settings = DIFFICULTY_SETTINGS[difficulty]
    speed = settings["speed"]
    gap = settings["gap"]
    pipe_distance = settings["pipe_distance"]

    ball_name, ball_color, ball_image_filename = (
        ball_skin if len(ball_skin) == 3 else (ball_skin[0], ball_skin[1], None)
    )
    ball = Ball(ball_color, ball_image_filename)

    # Load background/ground/pipe images ONCE for this session (not per frame)
    bg_image = assets_loader.load_image(paths.resource_path(BG_IMAGE_PATH), (WIDTH, HEIGHT))
    ground_image = assets_loader.load_image(paths.resource_path(GROUND_IMAGE_PATH), (WIDTH, GROUND_HEIGHT))
    Pipe.set_pipe_image(assets_loader.load_image(paths.resource_path(PIPE_IMAGE_PATH)))

    pipes = [Pipe(WIDTH + 100, gap, speed)]
    score = 0
    lives = STARTING_LIVES
    paused = False
    invincible_timer = 0

    running = True
    while running:
        dt = clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return {"score": score, "quit_to_menu": False, "quit_game": True}

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    paused = not paused
                elif event.key == pygame.K_SPACE and not paused:
                    ball.jump()
                    sound.play("jump")

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if paused:
                    resume_rect, quit_rect = draw_pause_overlay(screen)
                    if resume_rect.collidepoint(event.pos):
                        paused = False
                    elif quit_rect.collidepoint(event.pos):
                        return {"score": score, "quit_to_menu": True, "quit_game": False}
                else:
                    ball.jump()
                    sound.play("jump")

        if not paused:
            ball.update()

            if invincible_timer > 0:
                invincible_timer -= dt

            for pipe in pipes:
                pipe.update()

                if not pipe.passed and pipe.x + pipe.width < ball.x:
                    pipe.passed = True
                    score += 1
                    sound.play("score")

            pipes = [p for p in pipes if not p.off_screen()]

            if pipes and pipes[-1].x <= WIDTH - pipe_distance:
                pipes.append(Pipe(WIDTH, gap, speed))

            lost_a_life = False
            if invincible_timer <= 0:
                ball_rect = ball.get_rect()

                if ball.y + ball.radius >= HEIGHT - GROUND_HEIGHT:
                    lost_a_life = True
                elif ball.y - ball.radius <= 0:
                    lost_a_life = True
                else:
                    for pipe in pipes:
                        if ball_rect.colliderect(pipe.top_rect()) or ball_rect.colliderect(pipe.bottom_rect()):
                            lost_a_life = True
                            break

            if lost_a_life:
                lives -= 1
                if lives <= 0:
                    sound.play("game_over")
                    return {"score": score, "quit_to_menu": False, "quit_game": False}
                else:
                    sound.play("collision")
                    ball.reset()
                    pipes = [Pipe(WIDTH + 150, gap, speed)]
                    invincible_timer = 1200

        # --- Draw ---
        if bg_image:
            screen.blit(bg_image, (0, 0))
        else:
            screen.fill(SKY_BLUE)

        for pipe in pipes:
            pipe.draw(screen)

        if ground_image:
            screen.blit(ground_image, (0, HEIGHT - GROUND_HEIGHT))
        else:
            pygame.draw.rect(screen, (222, 184, 135), (0, HEIGHT - GROUND_HEIGHT, WIDTH, GROUND_HEIGHT))

        ball.draw(screen)
        draw_lives(screen, lives, STARTING_LIVES)
        draw_text(screen, f"Score: {score}", 30, BLACK, WIDTH - 120, 30)
        draw_text(screen, f"High Score: {high_score}", 22, BLACK, WIDTH - 120, 60)
        draw_text(screen, difficulty, 20, BLACK, WIDTH // 2, 25)

        if paused:
            draw_pause_overlay(screen)

        pygame.display.flip()

    return {"score": score, "quit_to_menu": False, "quit_game": False}