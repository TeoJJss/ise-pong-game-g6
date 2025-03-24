from ursina import Entity, color

class Obstacle(Entity):
    def __init__(self, position=(0, 0.26, 0), scale=(0.1, 0.05, 0.02), parent=None, color=color.black):
        super().__init__(
            model='cube',
            color=color,
            position=position,
            scale=scale,
            collider='box',
            parent=parent
        )