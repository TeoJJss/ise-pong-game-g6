from ursina import Entity, color, time, invoke, Audio
from config import ball_move_sound
import random

class Ball(Entity):
    def __init__(self, table, speed=1.5):
        super().__init__(
            parent=table,
            model='sphere',  # You can replace this with a custom model if needed
            color=color.brown,
            scale=0.05,
            position=(0, 3.71, -0.20),
            collider='sphere',  # More accurate collider for sphere
            shader='lit_with_shadows'  # Enable lighting/shadow shader
        )
        self.dx = 0.1
        self.dz = 0.2
        self.speed = speed
        self.just_bounced = False

        # Enable 3D shading and light reflection
        self.texture = 'white_cube'  # Gives a glossy 3D look with lighting

    def move(self):
        if ball_move_sound:
            Audio(ball_move_sound)
        self.x += self.dx * self.speed * time.dt
        self.z += self.dz * self.speed * time.dt

    def reset_position(self, wait=False):
        self.x = 0
        self.z = -0.20
        self.dx = 0
        self.dz = 0
        invoke(self.resume_movement, delay=1.5 if wait else 0)

    def resume_movement(self):
        # Randomly choose -1 or 1 for direction
        dx_direction = random.choice([-1, 1])
        dz_direction = random.choice([-1, 1])
        
        self.dx = 0.1 * dx_direction
        self.dz = 0.2 * dz_direction
