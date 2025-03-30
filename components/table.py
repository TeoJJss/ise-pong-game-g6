from ursina import Entity, color, Audio,destroy, Vec3
from config import whistle_sound, pong_sound
from random import uniform

class Table(Entity):
    def __init__(self):
        super().__init__(
            model='cube',
            color=color.green,
            scale=(10, 0.5, 14),
            position=(0, 0, 0),
            texture="white_cube"
        )
        self.line = Entity(parent=self, model='quad', scale=(0.88, 0.2, 0.1), position=(0, 3.5, -0.20))

    def check_bounds(self, ball, paddle_A, paddle_B):
        if abs(ball.x) > 0.4 and not ball.just_bounced:
            if pong_sound:
                Audio(pong_sound)
            ball.dx = -ball.dx
            ball.just_bounced = True  # Prevent re-triggering in the next frame
       
        if abs(ball.x) < 0.38: # Reset flag when ball moves away from bound
            ball.just_bounced = False

        if paddle_A.x > 0.32:
            # if pong_sound:
            #     Audio(pong_sound)
            paddle_A.x = 0.32
        elif paddle_A.x < -0.32:
            # if pong_sound:
            #     Audio(pong_sound)
            paddle_A.x = -0.32

        if paddle_B.x > 0.32:
            # if pong_sound:
            #     Audio(pong_sound)
            paddle_B.x = 0.32
        elif paddle_B.x < -0.32:
            # if pong_sound:
            #     Audio(pong_sound)
            paddle_B.x = -0.32
    
    def check_collision(self, ball, paddle_A, paddle_B, obstacle_entities, score_A, score_B):
        if ball.z > 0.25:
            if whistle_sound:
                Audio(whistle_sound)
            score_B += 1
            ball.reset_position(True)

        if ball.z < -0.65:
            if whistle_sound:
                Audio(whistle_sound)
            score_A += 1
            ball.reset_position(True)

        # Ball Collision with Paddles
        hit_info = ball.intersects()
        if hit_info.hit:
            if hit_info.entity == paddle_A or hit_info.entity == paddle_B or [obs for obs in obstacle_entities if hit_info.entity == obs]:
                if pong_sound:
                    Audio(pong_sound)
                ball.dz = -ball.dz
                self.animate_paddle_hit(hit_info.entity)
        
        return score_A, score_B
    
    def animate_paddle_hit(self, paddle):
        # Spark effect at paddle position (slightly above paddle for visibility)
        hit_position = paddle.world_position + Vec3(0, 0.05, 0)

        for _ in range(6):  # Number of sparks
            offset = Vec3(uniform(-0.03, 0.03), uniform(-0.03, 0.03), uniform(-0.03, 0.03))
            spark = Entity(
                model='sphere',
                color=color.yellow.tint(uniform(0.8, 1.0)),
                scale=0.15,
                position=hit_position + offset,
                add_to_scene_entities=True
            )
            # Animate spark scaling up slightly, then fading out
            spark.animate_scale(0.05, duration=0.1)
            spark.animate_color(color.clear, duration=0.15)
            destroy(spark, delay=0.2)