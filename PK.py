import os
import pygame
import sys
import random

# 定数定義
WIDTH = 800
HEIGHT = 600
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

class Player:
    def __init__(self):
        self.rect = pygame.Rect(WIDTH // 2 - 25, HEIGHT - 60, 50, 50)

class Ball:
    def __init__(self, player):
        self.rect = pygame.Rect(player.rect.centerx - 10, player.rect.top - 20, 20, 20)
        self.speed_x = 0
        self.speed_y = 0
        self.in_motion = False

    def reset_position(self, player):
        self.rect.x = player.rect.centerx - 10
        self.rect.y = player.rect.top - 20
        self.in_motion = False
        self.speed_x = 0
        self.speed_y = 0

    def update(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

class Goal:
    def __init__(self):
        self.rect = pygame.Rect(WIDTH // 2 - 175, 0, 350, 20)

class Keeper:
    def __init__(self, goal):
        self.width, self.height = 50, 20
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.positions = [
            goal.rect.centerx,
            goal.rect.left + self.width // 2,
            goal.rect.right - self.width // 2
        ]
        self.rect.y = goal.rect.bottom
        self.rect.centerx = self.positions[0]
        self.ball_stopped_time = None  # ボール停止時間
        self.has_moved_this_shot = False  # 一度だけ移動したか

    def move_once_random(self):
        """シュート開始時に1回だけランダムに移動"""
        self.rect.centerx = random.choice(self.positions)
        self.has_moved_this_shot = True

    def reset(self):
        """中央に戻す"""
        self.rect.centerx = self.positions[0]

def draw_text(surface, text, font, color, x, y):
    text_surf = font.render(text, True, color)
    surface.blit(text_surf, (x, y))

def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("簡易サッカーゲーム")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 48)

    player = Player()
    ball = Ball(player)
    goal = Goal()
    keeper = Keeper(goal)

    shoot_direction = 0
    goal_scored = False
    no_goal = False
    message_timer = 0

    running = True
    while running:
        current_time = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    shoot_direction = -1
                elif event.key == pygame.K_RIGHT:
                    shoot_direction = 1
                elif event.key == pygame.K_UP:
                    shoot_direction = 0
                elif event.key == pygame.K_SPACE:
                    if not ball.in_motion and not goal_scored and not no_goal:
                        ball.speed_y = -10
                        ball.speed_x = shoot_direction * 3
                        ball.in_motion = True
                        keeper.has_moved_this_shot = False
                        keeper.ball_stopped_time = None

        if ball.in_motion:
            ball.update()

            # シュート中、1回だけキーパーをランダムに動かす
            if not keeper.has_moved_this_shot:
                keeper.move_once_random()

            if ball.rect.colliderect(goal.rect):
                goal_scored = True
                ball.in_motion = False
                message_timer = current_time
                keeper.ball_stopped_time = current_time

            elif ball.rect.colliderect(keeper.rect):
                no_goal = True
                ball.in_motion = False
                message_timer = current_time
                keeper.ball_stopped_time = current_time

            elif ball.rect.top <= 0:
                ball.reset_position(player)
                keeper.ball_stopped_time = current_time

        else:
            # ボールが止まっている間の処理
            if keeper.ball_stopped_time:
                # 5秒経ったら中央に戻す
                if current_time - keeper.ball_stopped_time >= 3000:
                    keeper.reset()
                # 5秒以内はその場に止まる
            else:
                keeper.reset()

        # メッセージ表示後のリセット
        if goal_scored or no_goal:
            if current_time - message_timer > 1000:
                goal_scored = False
                no_goal = False
                ball.reset_position(player)
                # keeperは1秒経過まではそのまま

        # 描画処理
        screen.fill(GREEN)
        pygame.draw.rect(screen, BLACK, goal.rect)
        pygame.draw.rect(screen, WHITE, player.rect)
        pygame.draw.rect(screen, BLUE, keeper.rect)
        pygame.draw.ellipse(screen, RED, ball.rect)

        # 方向表示
        direction_text = {
            -1: "Direction: LEFT",
            0: "Direction: CENTER",
            1: "Direction: RIGHT"
        }[shoot_direction]
        draw_text(screen, direction_text, font, WHITE, 10, HEIGHT - 50)

        if goal_scored:
            draw_text(screen, "GOAL!", font, WHITE, WIDTH // 2 - 60, HEIGHT // 2)
        elif no_goal:
            draw_text(screen, "NO GOAL", font, WHITE, WIDTH // 2 - 80, HEIGHT // 2)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
