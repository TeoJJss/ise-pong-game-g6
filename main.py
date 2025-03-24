from components.table import Table
from components.paddle import Paddle
from components.ball import Ball
from components.opponent import Opponent
from components.obstacle import Obstacle
from ursina import Ursina, window, color, Text, camera, time, held_keys, invoke, application, Entity, Audio, destroy, print_on_screen
import json

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
app = Ursina(title = "Pong Game")
window.borderless = False  

# Game background
if not levels[current_level_key].get('background', ''):
    window.color = color.orange
else:
    background = Entity(
        model='quad',
        texture=levels[current_level_key]['background'],
        scale=(50, 30),         # Make it large enough to fill view
        position=(0, 0, 10),    # Push it behind the camera/table
        double_sided=True       # Make sure it's visible from both sides
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
    global game_started, game_time, score_A, score_B
    game_started = True
    game_time = 0
    score_A = 0
    score_B = 0
    ball.reset_position(wait=True)

def update():
    global score_A, score_B, game_time, game_started, current_level_key, point_text

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
        ball.speed = 2
    if game_time >= 20:
        ball.speed = 2.5

    ball.move()
    table.check_bounds(ball, paddle_A, paddle_B)
    score_A, score_B = table.check_collision(ball, paddle_A, paddle_B, obstacle_entities, score_A, score_B)
    # display points
    point_text.text = f"Bot : Player  = {score_A} : {score_B}"

    if score_A >= level_data['win_score']:
        if level_data['next'] is None:
            end_game("Bot Wins Final Level!", is_player_winner=False)
        else:
            proceed_to_next_level("Bot Wins!")
    elif score_B >= level_data['win_score']:
        if level_data['next'] is None:
            end_game("Player Wins Final Level!", is_player_winner=True)
        else:
            proceed_to_next_level("Player Wins!")

def proceed_to_next_level(message):
    global game_started, current_level_key, message_text
    game_started = False
    ball.dx = 0
    ball.dz = 0

    # Display win message and track it
    if message_text:
        message_text.enabled = False  # Hide previous message if any
    message_text = Text(text=message, scale=3, position=(0, 0), color=color.red, origin=(0,0))

    next_level = levels[current_level_key]['next']
    if next_level:
        current_level_key = next_level
        invoke(start_level, delay=2)
    else:
        end_game("All Levels Complete!", is_player_winner=True)


def start_level():
    global message_text, obstacle_entities, score_A, score_B

    score_A = 0
    score_B = 0

    if point_text:
        point_text.text = f"Bot : Player  = {score_A} : {score_B}"

    if message_text:
        message_text.enabled = False

    # Destroy old obstacles if any
    obstacle_entities = []
    for obs in obstacle_entities:
        destroy(obs)

    level_data = levels[current_level_key]
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
            caption_text.enabled = False
            start_game()

    display_caption(0)

# Start Level 1
start_level() 
invoke(show_captions, levels[current_level_key]['captions'], delay=1.5)
app.run()
