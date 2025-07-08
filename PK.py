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
        self.move_interval = 300  # ms
        self.goal = goal

    def update(self, current_time):
        if current_time - self.last_move_time > self.move_interval:
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
    size_manager = KeeperSizeManager()
    keeper = Keeper(goal, size_manager)

    shoot_direction = 0
    goal_scored = False
    no_goal = False
    message_timer = 0
    score = 0

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
                elif event.key == pygame.K_SPACE:
                    if not ball.in_motion and not goal_scored and not no_goal:
                        ball.speed_y = -10
                        ball.speed_x = shoot_direction * 3
                        ball.in_motion = True
                        keeper.last_move_time = current_time

        if ball.in_motion:
            ball.update()

            if ball.rect.colliderect(goal.rect):
                goal_scored = True
                score += 1
                ball.in_motion = False
                message_timer = current_time

            elif ball.rect.colliderect(keeper.rect):
                no_goal = True
                ball.in_motion = False
                message_timer = current_time

            elif ball.rect.top <= 0:
                ball.reset_position(player)

            keeper.update(current_time)
        else:
            keeper.reset()

        if goal_scored or no_goal:
            if current_time - message_timer > 2000:
                goal_scored = False
                no_goal = False
                ball.reset_position(player)
                keeper.reset()

        # 描画
        screen.fill(GREEN)
        pygame.draw.rect(screen, BLACK, goal.rect)
        pygame.draw.rect(screen, WHITE, player.rect)
        pygame.draw.rect(screen, BLUE, keeper.rect)
        pygame.draw.ellipse(screen, RED, ball.rect)

        direction_text = {
            -1: "Direction: LEFT",
            0: "Direction: CENTER",
            1: "Direction: RIGHT"
        }[shoot_direction]
        draw_text(screen, direction_text, font, WHITE, 10, HEIGHT - 50)
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
