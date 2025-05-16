from ursina import Entity, color, time

class Paddle(Entity):
    def __init__(self, table, x=0, z=0.22):
        super().__init__(
            parent=table,
            color=color.red,
            model='cube',
            scale=(0.20, 0.03, 0.05),
            position=(x, 3.7, z),
            collider='box',
            texture='red_paddle_texture.jpg', 
        )

    def move(self, direction):
        self.x += direction * time.dt

    def set_length(self, length):
        self.scale_x = length