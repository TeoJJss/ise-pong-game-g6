from ursina import Entity, color, time, invoke,Animation
from config import fire_animation
import random

class Ball(Entity):
    def __init__(self, table, speed=1.5):
        super().__init__(
            parent=table,
            model='sphere',  
            color=color.brown,
            scale=0.05,
            position=(0, 3.71, -0.20),
            collider='sphere'  
        )
        self.dx = 0.1
        self.dz = 0.2
        self.speed = speed
        self.just_bounced = False
        self.fire_effect_applied = False  

        self.texture = 'white_cube'  

    def apply_fire_texture(self):
        self.fire_effect = Animation(
            fire_animation,
            fps=10,
            loop=True,
            parent=self,
            scale=2,
            position=(0, 0.05, 0.5),
            billboard=True
        )

    def move(self):
        self.x += self.dx * self.speed * time.dt
        self.z += self.dz * self.speed * time.dt

        if self.speed >= 2 and not self.fire_effect_applied:
            invoke(self.apply_fire_texture)
            self.fire_effect_applied = True

    def reset_position(self, wait=False):
        self.x = 0
        self.z = -0.20
        self.dx = 0
        self.dz = 0
        invoke(self.resume_movement, delay=2.6 if wait else 0)

    def resume_movement(self):
        # Randomly choose -1 or 1 for direction
        dx_direction = random.choice([-1, 1])
        dz_direction = random.choice([-1, 1])
        
        self.dx = 0.1 * dx_direction
        self.dz = 0.2 * dz_direction
