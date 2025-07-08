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
        self.pos_x = float(self.rect.x)
        self.pos_y = float(self.rect.y)
        self.speed_x = 0.0
        self.speed_y = 0.0
        self.curve = 0
        self.in_motion = False
        self.curve_accel = 0.0  # 横方向加速度

    def reset_position(self, player):
        self.pos_x = float(player.rect.centerx - 10)
        self.pos_y = float(player.rect.top - 20)
        self.rect.x = int(self.pos_x)
        self.rect.y = int(self.pos_y)
        self.in_motion = False
        self.speed_x = 0.0
        self.speed_y = 0.0
        self.curve_accel = 0.0
        self.curve = 0

    def update(self):
        curve_strength=0.08
        # カーブの強さに応じて横方向の加速度を決定
        self.curve_accel = self.curve * curve_strength

        # 横速度に加速度を加算
        self.speed_x += self.curve_accel

        # 位置に速度を加算
        self.pos_x += self.speed_x
        self.pos_y += self.speed_y

        # rectに位置を反映（整数化）
        self.rect.x = int(self.pos_x)
        self.rect.y = int(self.pos_y)
        # self.rect.x += self.speed_x+ self.curve * curve_strength
        # self.rect.y += self.speed_y

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
        self.last_move_time = 0
        self.move_interval = 300  # ms

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
                        keeper.last_move_time = current_time
                elif event.key == pygame.K_z:
                    ball.curve = max(ball.curve -1,-3) # 左カーブ
                elif event.key == pygame.K_x:
                    ball.curve =min(ball.curve+1,3)    # 右カーブ
                elif event.key == pygame.K_c:
                    ball.curve = 0   # カーブなし（リセット）

        if ball.in_motion:
            ball.update()

            if ball.rect.colliderect(goal.rect):
                goal_scored = True
                ball.in_motion = False
                message_timer = current_time

            elif ball.rect.colliderect(keeper.rect):
                no_goal = True
                ball.in_motion = False
                message_timer = current_time

            elif ball.rect.bottom < 0 or ball.rect.right < 0 or ball.rect.left > WIDTH:
                no_goal = True
                ball.in_motion = False
                message_timer = current_time

            # キーパーの瞬間移動処理
            keeper.update(current_time)
        else:
            keeper.reset()

        # メッセージ表示後のリセット
        if goal_scored or no_goal:
            if current_time - message_timer > 2000:
                goal_scored = False
                no_goal = False
                ball.reset_position(player)
                keeper.reset()

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

        curve_text = {
            -3: "Curve: LEFT 3",
            -2: "Curve: LEFT 2",
            -1: "Curve: LEFT 1",
            0: "Curve: NONE",
            1: "Curve: RIGHT 1",
            2: "Curve: RIGHT 2",
            3: "Curve: RIGHT 3",
        }.get(ball.curve,"Curve:UNKNOWN")

        # カーブゲージ表示（バー）
        gauge_width = 200
        gauge_height = 20
        gauge_x = 10
        gauge_y = HEIGHT - 130

        # ゲージの背景（枠）
        pygame.draw.rect(screen, WHITE, (gauge_x, gauge_y, gauge_width, gauge_height), 2)

        # ゲージ中央線（カーブ0の位置）
        pygame.draw.line(screen, WHITE, (gauge_x + gauge_width // 2, gauge_y),
                        (gauge_x + gauge_width // 2, gauge_y + gauge_height), 1)

        # 実際のゲージバー
        bar_center = gauge_x + gauge_width // 2
        bar_length = (ball.curve / 3) * (gauge_width // 2)
        # pygame.draw.rect(screen, RED, (bar_center, gauge_y, bar_length, gauge_height))
        if bar_length > 0:
            pygame.draw.rect(screen, RED, (bar_center, gauge_y, bar_length, gauge_height))  # 右カーブ：赤
        elif bar_length < 0:
            pygame.draw.rect(screen, BLUE, (bar_center + bar_length, gauge_y, -bar_length, gauge_height))  # 左カーブ：青


        draw_text(screen, curve_text, font, WHITE, 10, HEIGHT - 100)

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