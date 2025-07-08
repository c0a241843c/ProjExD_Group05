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
YELLOW = (255, 255, 0)

class Player:
    def __init__(self):
        self.rect = pygame.Rect(WIDTH // 2 - 25, HEIGHT - 60, 50, 50)

class Ball:
    def __init__(self, player):
        self.rect = pygame.Rect(player.rect.centerx - 10, player.rect.top - 20, 20, 20)
        self.speed_x = 0
        self.speed_y = 0
        self.in_motion = False
        self.kantuu_dan = False  # ← 貫通弾かどうか

    def reset_position(self, player):
        self.rect.x = player.rect.centerx - 10
        self.rect.y = player.rect.top - 20
        self.in_motion = False
        self.speed_x = 0
        self.speed_y = 0
        self.kantuu_dan = False

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
        self.last_move_time = 0
        self.move_interval = 300
        self.kippaa_zyoukyou = "genzai"  # "genzai", "taoshi", "kieta"
        self.kippaa_haisoku_jikan = 0

    def update(self, current_time):
        if self.kippaa_zyoukyou == "genzai" and current_time - self.last_move_time > self.move_interval:
            self.rect.centerx = random.choice(self.positions)
            self.last_move_time = current_time

    def reset(self):
        self.rect.centerx = self.positions[0]
        self.kippaa_zyoukyou = "genzai"

    def destroy(self, current_time):
        self.kippaa_zyoukyou = "kieta"
        self.kippaa_haisoku_jikan = current_time

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
                        # 20%の確率で貫通弾にする
                        ball.kantuu_dan = random.random() < 0.2

        if ball.in_motion:
            ball.update()

            # ゴール判定を先に
            if ball.rect.colliderect(goal.rect):
                goal_scored = True
                ball.in_motion = False
                message_timer = current_time

            # ゴールしてない場合のキーパー判定
            elif ball.rect.colliderect(keeper.rect):
                if keeper.kippaa_zyoukyou == "genzai":
                    if ball.kantuu_dan:
                        keeper.destroy(current_time)  # 完全に消滅
                    else:
                        no_goal = True
                        ball.in_motion = False
                        message_timer = current_time

            elif ball.rect.top <= 0:
                ball.reset_position(player)

            keeper.update(current_time)
        else:
            if keeper.kippaa_zyoukyou == "genzai":
                keeper.reset()

        # メッセージ表示後のリセット
        if goal_scored or no_goal:
            if current_time - message_timer > 2000:
                goal_scored = False
                no_goal = False
                ball.reset_position(player)
                if keeper.kippaa_zyoukyou == "genzai":
                    keeper.reset()

        # 描画処理
        screen.fill(GREEN)
        pygame.draw.rect(screen, BLACK, goal.rect)
        pygame.draw.rect(screen, WHITE, player.rect)

        # キーパーの描画
        if keeper.kippaa_zyoukyou == "genzai":
            pygame.draw.rect(screen, BLUE, keeper.rect)
        elif keeper.kippaa_zyoukyou == "taoshi":
            pygame.draw.rect(screen, (100, 100, 100), keeper.rect)
        # "kieta" のときは描画しない

        # ボールの色（貫通弾は黄色）
        ball_color = YELLOW if ball.kantuu_dan else RED
        pygame.draw.ellipse(screen, ball_color, ball.rect)

        # 方向表示
        direction_text = {
            -1: "Direction: LEFT",
            0: "Direction: CENTER",
            1: "Direction: RIGHT"
        }[shoot_direction]
        draw_text(screen, direction_text, font, WHITE, 10, HEIGHT - 50)

        # メッセージ
        if goal_scored:
            draw_text(screen, "GOAL!", font, WHITE, WIDTH // 2 - 60, HEIGHT // 2)
        elif no_goal:
            draw_text(screen, "NO GOAL", font, WHITE, WIDTH // 2 - 80, HEIGHT // 2)
        elif keeper.kippaa_zyoukyou == "kieta":
            draw_text(screen, "KEEPER KESARETA!", font, YELLOW, WIDTH // 2 - 150, HEIGHT // 2)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()