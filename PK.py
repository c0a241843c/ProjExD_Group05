import os
import pygame
import sys
import random

os.chdir(os.path.dirname(os.path.abspath(__file__)))

pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("簡易サッカーゲーム")
clock = pygame.time.Clock()

WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

player = pygame.Rect(WIDTH//2 - 25, HEIGHT - 60, 50, 50)
ball = pygame.Rect(player.centerx - 10, player.top - 20, 20, 20)
ball_speed_y = 0
ball_speed_x = 0
ball_in_motion = False

goal = pygame.Rect(WIDTH//2 - 175, 0, 350, 20)

keeper_width, keeper_height = 50, 20
keeper = pygame.Rect(0, 0, keeper_width, keeper_height)

keeper_positions = [
    WIDTH//2 - keeper_width//2,   # 中央
    goal.left,                   # 左端
    goal.right - keeper_width    # 右端
]

keeper.y = goal.bottom
keeper.centerx = keeper_positions[0]

keeper_move_interval = 300  # 0.3秒ごとに動く
keeper_last_move_time = 0

font = pygame.font.SysFont(None, 48)

goal_scored = False
no_goal = False
message_timer = 0

shoot_direction = 0

while True:
    current_time = pygame.time.get_ticks()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                shoot_direction = -1
            elif event.key == pygame.K_RIGHT:
                shoot_direction = 1
            elif event.key == pygame.K_UP:
                shoot_direction = 0
            elif event.key == pygame.K_SPACE:
                if not ball_in_motion and not goal_scored and not no_goal:
                    ball_speed_y = -10
                    ball_speed_x = shoot_direction * 3
                    ball_in_motion = True
                    keeper_last_move_time = current_time  # シュート開始時にタイマーリセット

    if ball_in_motion:
        ball.x += ball_speed_x
        ball.y += ball_speed_y

        if ball.colliderect(goal):
            goal_scored = True
            ball_in_motion = False
            message_timer = current_time
        elif ball.colliderect(keeper):
            no_goal = True
            ball_in_motion = False
            message_timer = current_time

        if ball.top <= 0:
            ball_in_motion = False
            ball.y = player.top - 20
            ball.x = player.centerx - 10

        
        # キーパー動作
    if ball_in_motion:
        # 一定時間ごとに位置をランダムに切り替える（瞬間移動）
        if current_time - keeper_last_move_time > keeper_move_interval:
            new_pos = random.choice(keeper_positions)
            keeper.centerx = new_pos  # 瞬間移動でポジション切替
            keeper_last_move_time = current_time
    else:
        # ボール停止中は中央で静止
        keeper.centerx = keeper_positions[0]

    if goal_scored or no_goal:
        if current_time - message_timer > 2000:
            goal_scored = False
            no_goal = False
            ball.x = player.centerx - 10
            ball.y = player.top - 20
            keeper.centerx = keeper_positions[0]

    screen.fill(GREEN)
    pygame.draw.rect(screen, BLACK, goal)
    pygame.draw.rect(screen, WHITE, player)
    pygame.draw.rect(screen, BLUE, keeper)
    pygame.draw.ellipse(screen, RED, ball)

    direction_text = ""
    if shoot_direction == -1:
        direction_text = "Direction: LEFT"
    elif shoot_direction == 0:
        direction_text = "Direction: CENTER"
    elif shoot_direction == 1:
        direction_text = "Direction: RIGHT"

    dir_surface = font.render(direction_text, True, WHITE)
    screen.blit(dir_surface, (10, HEIGHT - 50))

    if goal_scored:
        text = font.render("GOAL!", True, WHITE)
        screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2))
    elif no_goal:
        text = font.render("NO GOAL", True, WHITE)
        screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2))

    pygame.display.flip()
    clock.tick(60)