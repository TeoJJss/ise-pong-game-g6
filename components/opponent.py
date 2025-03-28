from ursina import time, lerp, color
from components.paddle import Paddle 
import random

class Opponent(Paddle):
    def __init__(self, table, z, speed=2, chance_to_win=0.9):
        super().__init__(table=table, z=z)
        self.speed = speed  # Bot paddle 
        self.chance_to_miss = 1-chance_to_win
        self.color = color.blue

    def follow_ball(self, ball):
        if abs(ball.x - self.x) > 0.01:
            # Add a small delay or miss chance
            if random.random() > self.chance_to_miss:
                self.x = lerp(self.x, ball.x, self.speed * time.dt) # use linear interpolation to determine how much for paddle to move toward ball

        # Clamp to table boundaries
        self.x = max(min(self.x, 0.4), -0.4)

    def set_chance_to_win(self, value):
        self.chance_to_miss = 1-value