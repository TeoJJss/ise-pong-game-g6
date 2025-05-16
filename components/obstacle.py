from ursina import Entity, color, Audio, curve, invoke
from config import obstacle_spin_sound, obstacle_zoom_sound

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
        Audio(obstacle_spin_sound, volume=0.2)

        invoke(self.temporarily_disable, delay=1.1)

    def temporarily_disable(self):
        self.enabled = False
        invoke(self.revive, delay=15)

    def revive(self):
        self.enabled = True
        self.color = color.rgba(0, 255, 0, 255)
        self.rotation = (0, 0, 0)
        self.scale = (0.01, 0.01, 0.01)
        self.animate_scale((0.1, 0.05, 0.02), duration=1, curve=curve.out_bounce)
        Audio(obstacle_zoom_sound, volume=1.3)
        self.hit_count = 0

        invoke(setattr, self, 'color', color.rgba(0, 0, 0, 255), delay=1.5)