from ursina import Entity, color, time, Audio
# from config import paddle_move_sound

class Paddle(Entity):
    def __init__(self, table, x=0, z=0.22):
        super().__init__(
            parent=table,
            color=color.red,
            model='cube',
            scale=(0.20, 0.03, 0.05),
            position=(x, 3.7, z),
            collider='box'
        )

    def move(self, direction):
        # if paddle_move_sound:
        #     Audio(paddle_move_sound)
        self.x += direction * time.dt

    def set_length(self, length):
        self.scale_x = length