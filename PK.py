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
        self.pos_x = float(self.rect.x) 
        self.pos_y = float(self.rect.y)
        self.speed_x = 0.0
        self.speed_y = 0.0
        self.curve = 0 # カーブの強さ（-3から3まで）
        self.in_motion = False
        self.kantuu_dan = False
        self.curve_accel = 0.0  # 横方向加速度

    def reset_position(self, player):
        self.pos_x = float(player.rect.centerx - 10)
        self.pos_y = float(player.rect.top - 20)
        self.rect.x = int(self.pos_x)
        self.rect.y = int(self.pos_y)
        self.in_motion = False
        self.speed_x = 0.0
        self.speed_y = 0.0
        self.curve_accel = 0.0 # 横方向加速度のリセット
        self.curve = 0 # カーブの強さのリセット
        self.kantuu_dan = False

    def update(self):
        curve_strength=0.08 # カーブの強さを調整する係数
        self.curve_accel = self.curve * curve_strength  # カーブによる横方向の加速度

        self.speed_x += self.curve_accel # カーブによる横方向の加速度を速度に加算

        self.pos_x += self.speed_x  # 横方向の位置を更新
        self.pos_y += self.speed_y  # 縦方向の位置を更新

        self.rect.x = int(self.pos_x)  #x座標を更新
        self.rect.y = int(self.pos_y)  #y座標を更新

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
        self.kippaa_jyoukyou = "genzai"  # "genzai", "kieta"
        self.kippaa_haisoku_jikan = 0

    def update(self, current_time):
        if self.kippaa_jyoukyou == "genzai" and current_time - self.last_move_time > self.move_interval:
            self.rect.centerx = random.choice(self.positions)
            self.last_move_time = current_time

    def reset(self):
        self.rect.centerx = self.positions[0]
        self.kippaa_jyoukyou = "genzai"

    def destroy(self, current_time):
        """キーパーを破壊する関数"""
        self.kippaa_jyoukyou = "kieta"
        self.kippaa_haisoku_jikan = current_time

def draw_text(surface, text, font, color, x, y, center=True, bg_color=None):
    text_surf = font.render(text, True, color, bg_color)
    if center:
        text_rect = text_surf.get_rect(center=(x, y))
    else:
        text_rect = text_surf.get_rect(topleft=(x, y))
    surface.blit(text_surf, text_rect)

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

    # explosion.gif を読み込む（透過なし想定）
    explosion_img = pygame.image.load("fig/explosion.gif").convert()
    background_img = pygame.image.load("fig/fild.png").convert()
    background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))

    shoot_direction = 0
    goal_scored = False
    no_goal = False
    message_timer = 0
    score = 0
    q_pressed = False

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
                elif event.key == pygame.K_q:
                    if not ball.in_motion and score >= 1:
                        q_pressed = True
                elif event.key == pygame.K_SPACE:
                    if not ball.in_motion and not goal_scored and not no_goal:
                        ball.speed_y = -10
                        ball.speed_x = shoot_direction * 3
                        ball.in_motion = True
                        keeper.last_move_time = current_time
                        if q_pressed and score >= 3:
                            ball.kantuu_dan = True
                            score -= 2
                        else:
                            ball.kantuu_dan = False
                        q_pressed = False

        # ボール更新処理                elif event.key == pygame.K_z: # カーブの強さを調整
                    ball.curve = max(ball.curve -1,-3) # 左カーブ
                elif event.key == pygame.K_x: # カーブの強さを調整
                    ball.curve =min(ball.curve+1,3)# 右カーブ
                elif event.key == pygame.K_c: # カーブなし
                    ball.curve = 0   # カーブなし（リセット）

        if ball.in_motion:
            ball.update()

            if ball.rect.colliderect(goal.rect):
                goal_scored = True
                score += 1  # ← ゴール時にスコア加算
                ball.in_motion = False
                message_timer = current_time

            elif ball.rect.colliderect(keeper.rect):
                if keeper.kippaa_jyoukyou == "genzai":
                    if ball.kantuu_dan:
                        keeper.destroy(current_time)
                    else:
                        no_goal = True
                        ball.in_motion = False
                        message_timer = current_time

            elif ball.rect.bottom < 0 or ball.rect.right < 0 or ball.rect.left > WIDTH:
                no_goal = True
                ball.in_motion = False
                message_timer = current_time

            elif ball.rect.top <= 0:
                ball.reset_position(player)

            keeper.update(current_time)
        else:
            if keeper.kippaa_jyoukyou == "genzai":
                keeper.reset()

        # キーパー復活処理（3秒後）
        if keeper.kippaa_jyoukyou == "kieta":
            if current_time - keeper.kippaa_haisoku_jikan > 5000:
                keeper.reset()

        if goal_scored or no_goal:
            if current_time - message_timer > 2000:
                goal_scored = False
                no_goal = False
                ball.reset_position(player)
                if keeper.kippaa_jyoukyou == "genzai":
                    keeper.reset()

        # 描画
        screen.blit(background_img, (0, 0))
        pygame.draw.rect(screen, BLACK, goal.rect)
        pygame.draw.rect(screen, WHITE, player.rect)

        # キーパー描画
        if keeper.kippaa_jyoukyou == "genzai":
            pygame.draw.rect(screen, BLUE, keeper.rect)
        elif keeper.kippaa_jyoukyou == "kieta":
            screen.blit(explosion_img, keeper.rect)

        # ボール描画
        ball_color = YELLOW if ball.kantuu_dan else RED
        pygame.draw.ellipse(screen, ball_color, ball.rect)

        # UI描画
        direction_text = {
            -1: "Direction: LEFT",
            0: "Direction: CENTER",
            1: "Direction: RIGHT"
        }[shoot_direction]

        draw_text(screen, f"Score: {score}", font, WHITE, 20, 20, center=False)
        # カーブの強さ表示
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

        # カーブの強さに応じてバーの長さを調整
        if bar_length > 0: 
            pygame.draw.rect(screen, RED, (bar_center, gauge_y, bar_length, gauge_height))  # 右カーブ赤
        elif bar_length < 0: 
            pygame.draw.rect(screen, BLUE, (bar_center + bar_length, gauge_y, -bar_length, gauge_height))  # 左カーブ青

        draw_text(screen, curve_text, font, WHITE, 10, HEIGHT - 100)  
        draw_text(screen, direction_text, font, WHITE, 20, HEIGHT - 60, center=False)
        # メッセージ
        if goal_scored:
            draw_text(screen, "GOAL!", font, WHITE, WIDTH // 2 , HEIGHT // 2)
        elif no_goal:
            draw_text(screen, "NO GOAL", font, WHITE, WIDTH // 2 , HEIGHT // 2)
        elif keeper.kippaa_jyoukyou == "kieta":
            draw_text(screen, "!-------------KEEPER DESTROY------------!", font, YELLOW, WIDTH // 2, HEIGHT // 2)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()