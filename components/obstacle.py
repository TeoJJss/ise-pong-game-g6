from ursina import Entity, color, destroy, curve

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
        self.enabled = True  
        self.hit_count = 0

    def disable(self):
        self.enabled = False  

    def enable(self):
        self.enabled = True  
        
    def increment_hit_count(self):
        self.hit_count += 1
        if self.hit_count > 5:
            self.break_apart()

    def break_apart(self):
        self.animate_rotation((360, 360, 0), duration=1, curve=curve.in_out_bounce)
        self.animate_scale((0.01, 0.01, 0.01), duration=1, curve=curve.in_expo)
        self.animate_color(color.rgba(255, 0, 0, 0), duration=1, curve=curve.linear)

        destroy(self, delay=1.1)