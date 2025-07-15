import os
import pygame
import sys
import random

# 定数
WIDTH = 800
HEIGHT = 600
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# プレイヤー
class Player:
    def __init__(self):
        self.rect = pygame.Rect(WIDTH // 2 - 25, HEIGHT - 60, 50, 50)

# ボール（チャージ・カーブ対応）
class Ball:
    def __init__(self, player):
        self.rect = pygame.Rect(player.rect.centerx - 10, player.rect.top - 20, 20, 20)
        self.pos_x = float(self.rect.x)
        self.pos_y = float(self.rect.y)
        self.speed_x = 0.0
        self.speed_y = 0.0
        self.curve = 0
        self.curve_accel = 0.0
        self.in_motion = False
        self.kantuu_dan = False
        self.charging = False
        self.charge_start_time = 0
        self.max_charge_time = 1500  # 1.5秒

    def start_charge(self, now):
        self.charging = True
        self.charge_start_time = now

    def release_charge(self, now, direction):
        self.charging = False
        charge_duration = now - self.charge_start_time
        multiplier = 1 + min(charge_duration / self.max_charge_time, 1)
        self.speed_y = -10 * multiplier
        self.speed_x = direction * 3 * multiplier
        self.in_motion = True

    def reset_position(self, player):
        self.pos_x = float(player.rect.centerx - 10)
        self.pos_y = float(player.rect.top - 20)
        self.rect.topleft = (int(self.pos_x), int(self.pos_y))
        self.speed_x = 0.0
        self.speed_y = 0.0
        self.curve = 0
        self.curve_accel = 0.0
        self.in_motion = False
        self.kantuu_dan = False
        self.charging = False

    def update(self):
        self.curve_accel = self.curve * 0.08
        self.speed_x += self.curve_accel
        self.pos_x += self.speed_x
        self.pos_y += self.speed_y
        self.rect.x = int(self.pos_x)
        self.rect.y = int(self.pos_y)

    def draw_charge_gauge(self, screen):
        if self.charging:
            now = pygame.time.get_ticks()
            ratio = min((now - self.charge_start_time) / self.max_charge_time, 1)
            width = int(200 * ratio)
            pygame.draw.rect(screen, YELLOW, (WIDTH//2 - 100, HEIGHT - 40, width, 20))
            pygame.draw.rect(screen, WHITE, (WIDTH//2 - 100, HEIGHT - 40, 200, 20), 2)

# ゴール
class Goal:
    def __init__(self):
        self.rect = pygame.Rect(WIDTH // 2 - 175, 0, 350, 20)

# キーパーサイズマネージャ
class KeeperSizeManager:
    def __init__(self, base_width=50):
        self.base_width = base_width

    def get_width(self, score):
        return self.base_width * 4 if score >= 4 else self.base_width

# キーパー
class Keeper:
    def __init__(self, goal, size_manager):
        self.size_manager = size_manager
        self.height = 20
        self.width = self.size_manager.get_width(0)
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.y = goal.rect.bottom
        self.rect.centerx = WIDTH // 2
        self.kippaa_jyoukyou = "genzai"
        self.kippaa_haisoku_jikan = 0
        self.goal = goal
        self.last_move_time = 0
        self.move_interval = 300

    def update(self, now):
        if self.kippaa_jyoukyou == "genzai" and now - self.last_move_time > self.move_interval:
            pos = [WIDTH//2, self.goal.rect.left + self.rect.width//2, self.goal.rect.right - self.rect.width//2]
            self.rect.centerx = random.choice(pos)
            self.last_move_time = now

    def update_size(self, score):
        center = self.rect.centerx
        self.width = self.size_manager.get_width(score)
        self.rect.width = self.width
        self.rect.centerx = center

    def reset(self):
        self.rect.centerx = WIDTH // 2
        self.kippaa_jyoukyou = "genzai"

    def destroy(self, now):
        self.kippaa_jyoukyou = "kieta"
        self.kippaa_haisoku_jikan = now

# テキスト描画関数
def draw_text(surface, text, font, color, x, y, center=True, align_right=False):
    img = font.render(text, True, color)
    if center:
        rect = img.get_rect(center=(x, y))
    elif align_right:
        rect = img.get_rect(topright=(x, y))
    else:
        rect = img.get_rect(topleft=(x, y))
    surface.blit(img, rect)

# メイン
def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("サッカーゲーム")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 36)
    font = pygame.font.SysFont("meiryo", 24)

    player = Player()
    ball = Ball(player)
    goal = Goal()
    keeper = Keeper(goal, KeeperSizeManager())

    background = pygame.transform.scale(pygame.image.load("fig/fild.png"), (WIDTH, HEIGHT))
    explosion_img = pygame.image.load("fig/explosion.gif")

    shoot_dir = 0
    score = 0
    goal_scored = False
    no_goal = False
    q_pressed = False
    message_timer = 0

    running = True
    while running:
        now = pygame.time.get_ticks()
        keeper.update_size(score)

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_LEFT:
                    shoot_dir = -1
                elif e.key == pygame.K_RIGHT:
                    shoot_dir = 1
                elif e.key == pygame.K_UP:
                    shoot_dir = 0
                elif e.key == pygame.K_q and not ball.in_motion and score >= 3:
                    q_pressed = True
                elif e.key == pygame.K_s and not ball.in_motion:
                    ball.start_charge(now)
                elif e.key == pygame.K_z:
                    ball.curve = max(ball.curve - 1, -3)
                elif e.key == pygame.K_x:
                    ball.curve = min(ball.curve + 1, 3)
                elif e.key == pygame.K_c:
                    ball.curve = 0
                elif e.key == pygame.K_SPACE and not ball.in_motion:
                    ball.speed_y = -10
                    ball.speed_x = shoot_dir * 3
                    ball.in_motion = True
                    if q_pressed:
                        ball.kantuu_dan = True
                        score -= 2
                    q_pressed = False

            elif e.type == pygame.KEYUP:
                if e.key == pygame.K_s and ball.charging:
                    ball.release_charge(now, shoot_dir)
                    if q_pressed:
                        ball.kantuu_dan = True
                        score -= 2
                    q_pressed = False

        if ball.in_motion:
            ball.update()
            keeper.update(now)

            if ball.rect.colliderect(goal.rect):
                score += 1
                goal_scored = True
                ball.in_motion = False
                message_timer = now
            elif ball.rect.colliderect(keeper.rect):
                if keeper.kippaa_jyoukyou == "genzai":
                    if ball.kantuu_dan:
                        keeper.destroy(now)
                    else:
                        no_goal = True
                        ball.in_motion = False
                        message_timer = now
            elif ball.rect.top < 0 or ball.rect.right < 0 or ball.rect.left > WIDTH:
                no_goal = True
                ball.in_motion = False
                message_timer = now
        else:
            if goal_scored or no_goal:
                if now - message_timer > 2000:
                    goal_scored = False
                    no_goal = False
                    ball.reset_position(player)
                    keeper.reset()

        if keeper.kippaa_jyoukyou == "kieta" and now - keeper.kippaa_haisoku_jikan > 5000:
            keeper.reset()

        # 画面描画
        screen.blit(background, (0, 0))
        pygame.draw.rect(screen, BLACK, goal.rect)
        pygame.draw.rect(screen, WHITE, player.rect)

        if keeper.kippaa_jyoukyou == "genzai":
            pygame.draw.rect(screen, BLUE, keeper.rect)
        else:
            screen.blit(explosion_img, keeper.rect)

        ball_color = YELLOW if ball.kantuu_dan else RED
        pygame.draw.ellipse(screen, ball_color, ball.rect)
        ball.draw_charge_gauge(screen)

        draw_text(screen, f"Score: {score}", font, WHITE, 20, 20, center=False)
        curve_desc = {
            -3: "LEFT +3", -2: "LEFT +2", -1: "LEFT +1",
            0: "NONE", 1: "RIGHT +1", 2: "RIGHT +2", 3: "RIGHT +3"
        }[ball.curve]
        draw_text(screen, f"カーブ: {curve_desc}", font, WHITE, 20, 60, center=False)
        draw_text(screen, f"方向: {['LEFT','CENTER','RIGHT'][shoot_dir+1]}", font, WHITE, 20, 100, center=False)

        # 操作ガイド（右下）
        guide_lines = [
            "[SPACE] 通常シュート",
            "[S 長押し] チャージシュート",
            "[Z/X/C] カーブ左/右/リセット",
            "[Q] 貫通弾（スコア3必要）"
        ]
        line_height = 28
        
        total_height = len(guide_lines) * line_height
        bottom_margin = 40
        right_margin = 20

        for i, text in enumerate(reversed(guide_lines)):
            y = HEIGHT - bottom_margin - (line_height * i)
            draw_text(screen, text, font, WHITE, WIDTH - right_margin, y, center=False, align_right=True)

        if goal_scored:
            draw_text(screen, "GOAL!", font, WHITE, WIDTH//2, HEIGHT//2)
        elif no_goal:
            draw_text(screen, "NO GOAL", font, WHITE, WIDTH//2, HEIGHT//2)
        elif keeper.kippaa_jyoukyou == "kieta":
            draw_text(screen, "KEEPER DESTROYED!", font, YELLOW, WIDTH//2, HEIGHT//2)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
