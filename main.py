from components.table import Table
from components.paddle import Paddle
from components.ball import Ball
from components.opponent import Opponent
from components.obstacle import Obstacle
from ursina import Ursina, window, color, Text, camera, time, held_keys, invoke, application, Entity, Audio, destroy, load_texture, curve
import json
from config import *

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
paused = False
pause_text = None
background_entity = None

# Game init
app = Ursina(title=APP_TITLE, icon=APP_ICON)
window.resizable = False
window.borderless = False

def start_game():
    global game_started, game_time, score_A, score_B, ball
    game_started = True
    game_time = 0
    score_A = 0
    score_B = 0
    ball.reset_position(wait=True)
    ball.speed = levels[current_level_key].get('ball_speed', 1)

def input(key):
    if key == "escape":
        toggle_pause()

def update():   
    global score_A, score_B, game_time, game_started, current_level_key, point_text, obstacle_entities

    if paused or not game_started or game_over:  # if game is paused OR not started OR already end, stop the game logic
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
        ball.speed = max(2.2, levels[current_level_key].get('ball_speed', 1) * 2.2)

    ball.move()
    table.check_bounds(ball, paddle_A, paddle_B)

    # Check score changes and trigger effects
    previous_score_A = score_A
    previous_score_B = score_B

    score_A, score_B = table.check_collision(ball, paddle_A, paddle_B, obstacle_entities, score_A, score_B)

    if score_A > previous_score_A:
        Audio(whistle_sound)
        flash_screen(flash_color=color.rgba(252/255, 3/255, 3/255, 0.4))
        camera.shake(duration=0.2, magnitude=0.02)

    elif score_B > previous_score_B:
        Audio(whistle_sound)
        flash_screen(flash_color=color.rgba(15/255, 252/255, 3/255, 0.4))
        camera.shake(duration=0.2, magnitude=0.02)

    # display updated points
    point_text.text = f"Bot : Player  = {score_A} : {score_B}"

    # check win condition
    if score_A >= level_data['win_score']:
        proceed_to_next_level("Bot Wins!", is_player_winner=False)
    elif score_B >= level_data['win_score']:
        if level_data['next'] is None:
            end_game("Player Wins Final Level!", is_player_winner=True)
        else:
            proceed_to_next_level("Player Wins!", is_player_winner=True)


def toggle_pause():
    global paused, pause_text
    paused = not paused

    if paused:
        pause_text = Text(
            text="PAUSED",
            scale=3,
            position=(0, 0.1),
            color=color.red,
            origin=(0, 0),
            font=kanit_font,
            outline_color=color.black,
            outline_thickness=1.5,
            shadow=True
        )
    else:
        if pause_text:
            destroy(pause_text)
            pause_text = None

def proceed_to_next_level(message, is_player_winner):
    global game_started, current_level_key, message_text, score_A, score_B, game_time, caption_text
    game_started = False
    ball.dx = 0
    ball.dz = 0

    level_data = levels[current_level_key]
    captions = level_data['win_captions'] if is_player_winner else level_data['lose_captions']

    if victory_sound and is_player_winner:
        Audio(victory_sound)
    elif lost_sound and not is_player_winner:
        Audio(lost_sound)

    def display_end_level_caption(index):
        global caption_text, current_level_key
        if index < len(captions):
            if caption_text:
                caption_text.enabled = False
            caption_text = Text(
                text=captions[index],
                scale=1.5,
                position=(0, 0.4),
                color=color.white,
                background=True,
                origin=(0, 0),
                font=kanit_font,
                outline_color=color.black,
                outline_thickness=1.5,
                shadow=True
            )
            invoke(display_end_level_caption, index + 1, delay=CAPTION_DELAY)
        else:
            if caption_text:
                caption_text.enabled = False
            if is_player_winner:
                next_level = levels[current_level_key]['next']
                if next_level:
                    current_level_key = next_level
                    invoke(start_level, delay=0.8)
                else:
                    end_game("All Levels Complete!", is_player_winner=True)
            else:
                invoke(start_level, delay=0.5) # Restart current level if player loses

    display_end_level_caption(0)

def start_level():
    global message_text, obstacle_entities, score_A, score_B, point_text, background_entity, bg_music, ball

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
        if background_entity:
            destroy(background_entity)
            background_entity = None
    else:
        bg_img = load_texture(level_data['background'], filtering=0)
        if bg_img:
            window_aspect = window.aspect_ratio
            texture_aspect = bg_img.width / bg_img.height if bg_img.height > 0 else 1

            if window_aspect > texture_aspect:
                # Window is wider, scale width to cover
                scale_x = window_aspect
                scale_y = 1.0
            else:
                # Window is taller, scale height to cover
                scale_x = 1.0
                scale_y = 1.0 / window_aspect * texture_aspect

            # Slightly increase the scale to ensure full coverage
            coverage_multiplier = 1.05  # Adjust this value if needed

            new_scale_x = scale_x * 33 * coverage_multiplier  # Adjust base scale (20) as needed
            new_scale_y = scale_y * 20 * coverage_multiplier

            if background_entity:
                background_entity.texture = bg_img
                background_entity.scale = (new_scale_x, new_scale_y)
            else:
                background_entity = Entity(
                    model='quad',
                    texture=bg_img,
                    scale=(new_scale_x, new_scale_y),
                    position=(0, -7, 10),
                    double_sided=True,
                )
            start_level.background_entity = background_entity # Store for potential later use
        else:
            window.color = color.gray  # Fallback if background image fails to load

    # Update background music (rest of your start_level code remains the same)
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

    if victory_sound and is_player_winner:
        Audio(victory_sound)
    elif lost_sound and not is_player_winner:
        Audio(lost_sound)

    # Show captions before quitting
    def display_caption(index):
        global caption_text
        if index < len(captions):
            if caption_text:
                caption_text.enabled = False
            caption_text = Text(
                text=captions[index],
                scale=1.5,
                position=(0, 0.42),
                color=color.white,
                background=True,
                origin=(0, 0),
                font=kanit_font,
                outline_color=color.black,
                outline_thickness=1,
                shadow=True
            )
            invoke(display_caption, index + 1, delay=CAPTION_DELAY)
        else:
            if caption_text:
                caption_text.enabled = False
            invoke(application.quit, delay=2.5)

    display_caption(0)

def show_captions(level_captions):
    def display_caption(index):
        global caption_text
        if index < len(level_captions):
            if caption_text:
                caption_text.enabled = False
            if index == len(level_captions) - 1:
                if game_start_sound:
                    Audio(game_start_sound)
            caption_text = Text(
                text=level_captions[index],
                scale=1.2,
                position=(0, 0.42),
                color=color.white,
                background=True,
                origin=(0, 0),
                font=kanit_font,
                outline_color=color.black,
                outline_thickness=1,
                shadow=True
            )
            invoke(display_caption, index + 1, delay=2.6)
        else:
            if caption_text:
                caption_text.enabled = False
            start_game()

    display_caption(0)

def flash_screen(flash_color):
    flash = Entity(
        model='quad',
        color=flash_color,
        scale=(40, 22),
        position=(0, 0, -1),  # Set to a layer in front of everything
        parent=camera.ui
    )
    
    # Fade it out smoothly
    flash.animate_color(
        color.rgba(flash_color[0], flash_color[1], flash_color[2], 0),
        duration=2,
        curve=curve.linear
    )

    destroy(flash, delay=1.1)

# Game objects (created after app initialization)
table = Table()
paddle_A = Opponent(table=table, z=0.22)
paddle_B = Paddle(table=table, z=-0.62)
Text(text="Bot", scale=1, position=(-0.05, 0.32), background = True, outline_color=color.black, outline_thickness=1,font=roboto_font)
Text(text="Player", scale=1, position=(-0.05, -0.42), background = True, outline_color=color.black, outline_thickness=1,font=roboto_font)
point_text = Text(text=f"Bot : Player  = {score_A} : {score_B}", position=(-0.65, .35), scale=1.3, color=color.white, outline_color=color.blue, outline_thickness=1, shadow=True, font=roboto_font)
pause_inst = Text(text="PRESS ESC to PAUSE/RESUME", position=(0.25, .35), scale=1.3, color=color.white, outline_color=color.blue, outline_thickness=1, shadow=True, font=roboto_font)
ball = Ball(table=table)
camera.position = (0, 15, -26)
camera.rotation_x = 30

# Start Level 1
start_level()
app.run()