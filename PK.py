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
        self.kantuu_dan = False

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

class KeeperSizeManager:#新しいクラス
    def __init__(self, base_width=50):
        self.base_width = base_width

    def get_width(self, score):#スコアが４以上でキーパーのサイズを四倍に
        return self.base_width * 4 if score >= 4 else self.base_width

class Keeper:
    def __init__(self, goal, size_manager):
        self.size_manager = size_manager
        self.height = 20
        self.width = self.size_manager.get_width(0)
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.y = goal.rect.bottom
        self.rect.centerx = WIDTH // 2
        self.last_move_time = 0
        self.move_interval = 300
        self.kippaa_jyoukyou = "genzai"  # "genzai", "kieta"
        self.kippaa_haisoku_jikan = 0
        self.goal = goal
        
    def update(self, current_time):
        if self.kippaa_jyoukyou == "genzai" and current_time - self.last_move_time > self.move_interval:
            positions = [
                WIDTH // 2,
                self.goal.rect.left + self.rect.width // 2,
                self.goal.rect.right - self.rect.width // 2
            ]
            self.rect.centerx = random.choice(positions)
            self.last_move_time = current_time

    def reset(self):
        self.rect.centerx = WIDTH // 2

    def update_size(self, score):
        current_center = self.rect.centerx
        self.width = self.size_manager.get_width(score)
        self.rect.width = self.width
        self.rect.x = current_center - self.width // 2
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
    size_manager = KeeperSizeManager()
    keeper = Keeper(goal, size_manager)

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
        keeper.update_size(score)  # キーパーのサイズ更新

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
                        keeper.has_moved_this_shot = False
                        #停止タイマーリセット
                        keeper.ball_stopped_time = None

                        if q_pressed and score >= 3:
                            ball.kantuu_dan = True
                            score -= 2
                        else:
                            ball.kantuu_dan = False
                        q_pressed = False

        # ボール更新処理
        if ball.in_motion:
            ball.update()

            #移動していなければ1回だけランダム移動
            if not keeper.has_moved_this_shot:
                keeper.move_once_random()

            if ball.rect.colliderect(goal.rect):
                goal_scored = True
                score += 1
                ball.in_motion = False
                message_timer = current_time
                keeper.ball_stopped_time = current_time  #停止時間を記録

            elif ball.rect.colliderect(keeper.rect):
                if keeper.kippaa_jyoukyou == "genzai":
                    if ball.kantuu_dan:
                        keeper.destroy(current_time)
                    else:
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
                ball.x = player.centerx - 10
                if keeper.kippaa_jyoukyou == "genzai":
                    ball.y = player.top - 20

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
