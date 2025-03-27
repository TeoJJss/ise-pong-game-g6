from components.table import Table
from components.paddle import Paddle
from components.ball import Ball
from components.opponent import Opponent
from components.obstacle import Obstacle
from ursina import Ursina, window, color, Text, camera, time, held_keys, invoke, application, Entity, Audio, destroy, print_on_screen
import json
from config import APP_TITLE, APP_ICON

# Dictionary Levels
levels = json.load(open("./levels.json",))

current_level_key = 'level_1'
game_started = False
caption_text = None
message_text = None
game_time = 0
score_A = 0
score_B = 0
game_over = False
obstacle_entity = None
point_text = None

# Game init
app = Ursina(title = APP_TITLE, icon=APP_ICON)
window.borderless = False

# Game background
if not levels[current_level_key].get('background', ''):
    window.color = color.orange
else:
    background = Entity(
        model='quad',
        texture=levels[current_level_key]['background'],
        scale=(50, 30),         # Make it large enough to fill view
        position=(0, 0, 10),     # Push it behind the camera/table
        double_sided=True         # Make sure it's visible from both sides
    )

# GAme background music
if levels[current_level_key].get('background_music', ''):
    bg_music = Audio(levels[current_level_key]['background_music'], loop=True, autoplay=True, volume=0.5)

# Game objects
table = Table()
paddle_A = Opponent(table=table, z=0.22)
paddle_B = Paddle(table=table, z=-0.62)
Text(text="Bot", scale=2, position=(-0.1, 0.32))
Text(text="Player", scale=2, position=(-0.1, -0.4))
point_text = Text(text=f"Bot : Player  = {score_A} : {score_B}", position=(-0.85, .45), scale=1, color=color.white)
ball = Ball(table=table)
camera.position = (0, 15, -26)
camera.rotation_x = 30

def start_game():
    global game_started, game_time, score_A, score_B, ball
    game_started = True
    game_time = 0
    score_A = 0
    score_B = 0
    ball.reset_position(wait=True)
    ball.speed = levels[current_level_key].get('ball_speed', 1)

def update():
    global score_A, score_B, game_time, game_started, current_level_key, point_text, obstacle_entities

    if not game_started or game_over:
        return

    level_data = levels[current_level_key]
    # paddle_A.set_length(level_data['paddle_length'])
    paddle_B.set_length(level_data['paddle_length'])
    paddle_A.set_chance_to_win(level_data['bot_accuracy'])

    paddle_A.follow_ball(ball)
    paddle_B.move(held_keys['right arrow'] - held_keys['left arrow'])

    game_time += time.dt
    if game_time >= 10:
        ball.speed = max(2, levels[current_level_key].get('ball_speed', 1) * 2)
    if game_time >= 20:
        ball.speed = max(2.5, levels[current_level_key].get('ball_speed', 1) * 2.5)

    ball.move()
    table.check_bounds(ball, paddle_A, paddle_B)
    score_A, score_B = table.check_collision(ball, paddle_A, paddle_B, obstacle_entities, score_A, score_B)
    # display points
    point_text.text = f"Bot : Player  = {score_A} : {score_B}"

    if score_A >= level_data['win_score']:
        proceed_to_next_level("Bot Wins!", is_player_winner=False)
    elif score_B >= level_data['win_score']:
        if level_data['next'] is None:
            end_game("Player Wins Final Level!", is_player_winner=True)
        else:
            proceed_to_next_level("Player Wins!", is_player_winner=True)

def proceed_to_next_level(message, is_player_winner):
    global game_started, current_level_key, message_text, score_A, score_B, game_time, caption_text
    game_started = False
    ball.dx = 0
    ball.dz = 0

    level_data = levels[current_level_key]
    captions = level_data['win_captions'] if is_player_winner else level_data['lose_captions']

    def display_end_level_caption(index):
        global caption_text, current_level_key
        if index < len(captions):
            if caption_text:
                caption_text.enabled = False
            caption_text = Text(
                text=captions[index],
                scale=2,
                position=(0, 0.4),
                color=color.azure,
                background=True,
                origin=(0, 0),
                font='./assets/font/Kanit-Bold.ttf',
                outline_color=color.black,
                outline_thickness=1.5,
                shadow=True
            )
            invoke(display_end_level_caption, index + 1, delay=1.5)
        else:
            if caption_text:
                caption_text.enabled = False
            if is_player_winner:
                next_level = levels[current_level_key]['next']
                if next_level:
                    current_level_key = next_level
                    invoke(start_level, delay=0.5)
                else:
                    end_game("All Levels Complete!", is_player_winner=True)
            else:
                invoke(start_level, delay=0.5) # Restart current level if player loses

    display_end_level_caption(0)

def start_level():
    global message_text, obstacle_entities, score_A, score_B, point_text, background, bg_music, ball

    score_A = 0
    score_B = 0

    if point_text:
        point_text.text = f"Bot : Player  = {score_A} : {score_B}"

    if message_text:
        message_text.enabled = False

    # Destroy old obstacles
    if hasattr(start_level, 'obstacle_entities'):
        for obs in start_level.obstacle_entities:
            destroy(obs)
        start_level.obstacle_entities = []
    else:
        start_level.obstacle_entities = []

    level_data = levels[current_level_key]

    # Update background
    if not level_data.get('background', ''):
        window.color = color.orange
        if hasattr(start_level, 'background_entity'):
            destroy(start_level.background_entity)
            del start_level.background_entity
    else:
        if hasattr(start_level, 'background_entity'):
            start_level.background_entity.texture = level_data['background']
        else:
            start_level.background_entity = Entity(
                model='quad',
                texture=level_data['background'],
                scale=(50, 30),
                position=(0, 0, 10),
                double_sided=True
            )

    # Update background music
    if level_data.get('background_music', ''):
        if hasattr(start_level, 'bg_music'):
            start_level.bg_music.clip = level_data['background_music']
            if not start_level.bg_music.playing:
                start_level.bg_music.play()
        else:
            start_level.bg_music = Audio(level_data['background_music'], loop=True, autoplay=True, volume=0.5)
    else:
        if hasattr(start_level, 'bg_music'):
            start_level.bg_music.stop()
            destroy(start_level.bg_music)
            del start_level.bg_music

    obstacle_ls = level_data.get('obstacle', [])
    obstacle_entities = []
    for obstacle_info in obstacle_ls:
        if obstacle_info.get('enabled', False):
            obs = Obstacle(
                position=tuple(obstacle_info.get('position', [0, 0.26, 0])),
                scale=tuple(obstacle_info.get('scale', [0.1, 0.05, 0.02])),
                parent=table
            )
            obstacle_entities.append(obs)
    start_level.obstacle_entities = obstacle_entities # Store for cleanup

    show_captions(level_data['captions'])

def end_game(message, is_player_winner):
    global game_started, game_over, message_text, caption_text
    game_started = False
    game_over = True

    if message_text:
        message_text.enabled = False
    message_text = Text(text=message, scale=3, position=(0, 0), color=color.red, origin=(0, 0))

    ball.dx = 0
    ball.dz = 0

    level_data = levels[current_level_key]

    # Choose the correct caption list
    captions = level_data['win_captions'] if is_player_winner else level_data['lose_captions']

    # Show captions before quitting
    def display_caption(index):
        global caption_text
        if index < len(captions):
            if caption_text:
                caption_text.enabled = False
            caption_text = Text(
                text=captions[index],
                scale=2,
                position=(0, 0.4),
                color=color.azure,
                background=True,
                origin=(0, 0),
                outline_color=color.black,
                outline_thickness=1.5,
                shadow=True
            )
            invoke(display_caption, index + 1, delay=1.5)
        else:
            if caption_text:
                caption_text.enabled = False
            invoke(application.quit, delay=1.5)

    display_caption(0)

def show_captions(level_captions):
    def display_caption(index):
        global caption_text
        if index < len(level_captions):
            if caption_text:
                caption_text.enabled = False
            caption_text = Text(
                text=level_captions[index],
                scale=2,
                position=(0, 0.4),
                color=color.azure,
                background=True,
                origin=(0, 0),
                font='./assets/font/Kanit-Bold.ttf',
                outline_color=color.black,
                outline_thickness=1.5,
                shadow=True
            )
            invoke(display_caption, index + 1, delay=2)
        else:
            if caption_text:
                caption_text.enabled = False
            start_game()

    display_caption(0)

# Start Level 1
start_level()
app.run()