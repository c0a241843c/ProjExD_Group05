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
            WIDTH // 2 - self.width // 2,
            goal.rect.left,
            goal.rect.right - self.width
        ]
        self.rect.y = goal.rect.bottom
        self.rect.centerx = self.positions[0]
        #ボール停止時間、シュートごとの移動制御
        self.ball_stopped_time = None
        self.has_moved_this_shot = False

    def update(self, current_time):
        if current_time - self.last_move_time > self.move_interval:
            self.rect.centerx = random.choice(self.positions)
            self.last_move_time = current_time

    def reset(self):
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
    score = 0  # ← 得点カウント

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
                        #停止タイマーリセット
                        keeper.ball_stopped_time = None


        if ball.in_motion:
            ball.update()

            #移動していなければ1回だけランダム移動
            if not keeper.has_moved_this_shot:
                keeper.move_once_random()

            if ball.rect.colliderect(goal.rect):
                goal_scored = True
                score += 1  # ← ゴール時にスコア加算
                ball.in_motion = False
                message_timer = current_time
                keeper.ball_stopped_time = current_time  #停止時間を記録

            elif ball.rect.colliderect(keeper.rect):
                no_goal = True
                ball.in_motion = False
                message_timer = current_time
                keeper.ball_stopped_time = current_time  #停止時間を記録

            elif ball.rect.top <= 0:
                ball.reset_position(player)
                keeper.ball_stopped_time = current_time  #停止時間を記録

            keeper.update(current_time)
        else:
            #ボールが止まっている間は5秒待つ
            if keeper.ball_stopped_time:
                if current_time - keeper.ball_stopped_time >= 5000:
                    keeper.reset()  #5秒経過したら中央へ
                #5秒未満はそのままの位置に止まる
            else:
                keeper.reset()

        if goal_scored or no_goal:
            if current_time - message_timer > 2000:
                goal_scored = False
                no_goal = False
                ball.x = player.centerx - 10
                ball.y = player.top - 20

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

        # スコア表示
        draw_text(screen, f"Score: {score}", font, WHITE, 10, 10)

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