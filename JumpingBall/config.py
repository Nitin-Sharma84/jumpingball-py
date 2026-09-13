# config.py
# All game constants live here. Change values here to tune the game.

WIDTH = 1000
HEIGHT = 600
FPS = 60

# Colors (R, G, B)
WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
SKY_BLUE = (135, 206, 250)
GREEN = (60, 180, 75)
DARK_GREEN = (30, 120, 40)
RED = (220, 50, 50)
YELLOW = (240, 200, 40)
GRAY = (100, 100, 100)
LIGHT_GRAY = (230, 230, 230)
BROWN=(150, 75, 0)

# Ball physics
GRAVITY = 0.7
JUMP_STRENGTH = -9
BALL_RADIUS = 27
BALL_START_X = 200

# Ground
GROUND_HEIGHT = 60

# Pipes
PIPE_WIDTH = 70

# Difficulty settings.
# "pipe_distance" is the horizontal PIXEL distance between consecutive pipes.
# Using a fixed distance (not a timer) means the gap between pipes is always
# exactly the same, no matter how the frame rate behaves.
DIFFICULTY_SETTINGS = {
    "Easy":   {"speed": 6, "gap": 180, "pipe_distance": 310},
    "Medium": {"speed": 7, "gap": 170, "pipe_distance": 290},
    "Hard":   {"speed": 8, "gap": 160, "pipe_distance": 275},
}

STARTING_LIVES = 3

# Ball skins used before real images are added.
# Each entry: (display_name, color)
BALL_SKINS = [
    ("Ball 1", (220, 60, 60), "ball1.png"),
    ("Ball 2", (60, 120, 220), "ball2.png"),
    ("Ball 3", (240, 200, 40), "ball3.png"),
    ("Ball 4", (60, 180, 75), "ball4.png"),
]

DB_PATH = "data/jumping_ball.db"
