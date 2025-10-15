import pygame
import sys
import math
import json
import os
import random

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SCALED)
pygame.display.set_caption("Bullet Hell")
clock = pygame.time.Clock()
FPS = 60

def load_scaled(path, scale):
    raw = pygame.image.load(path).convert_alpha()
    size = (raw.get_width() * scale, raw.get_height() * scale)
    return pygame.transform.scale(raw, size)

player_image = load_scaled("assets/player.png", 4)
enemy_image = load_scaled("assets/enemy.png", 6)
ball_image = load_scaled("assets/ball.png", 3)
shield_image = load_scaled("assets/shield.png", 5)
bg_image = pygame.transform.scale(pygame.image.load("assets/bg.jpg").convert(), (WIDTH, HEIGHT))
powerup_image = load_scaled("assets/powerup.png", 3)

font = pygame.font.SysFont("consolas", 32)
small_font = pygame.font.SysFont("consolas", 24)

SCORE_FILE = "highscores.json"

def save_score(name, score):
    data = []
    if os.path.exists(SCORE_FILE):
        with open(SCORE_FILE, "r") as f:
            try:
                data = json.load(f)
            except:
                data = []
    found = False
    for entry in data:
        if entry["name"].lower() == name.lower():
            found = True
            if score > entry["score"]:
                entry["score"] = score
            break
    if not found:
        data.append({"name": name, "score": score})
    with open(SCORE_FILE, "w") as f:
        json.dump(data, f)

def load_scores():
    if os.path.exists(SCORE_FILE):
        with open(SCORE_FILE, "r") as f:
            try:
                return json.load(f)
            except:
                return []
    return []

def draw_button(text, x, y, w, h):
    rect = pygame.Rect(x, y, w, h)
    pygame.draw.rect(screen, (50, 50, 50), rect)
    pygame.draw.rect(screen, (255, 255, 255), rect, 2)
    label = font.render(text, True, (255, 255, 255))
    screen.blit(label, (x + (w - label.get_width()) // 2, y + (h - label.get_height()) // 2))
    return rect

MENU = "menu"
GAME = "game"
LOSE = "lose"
NAME_ENTRY = "name_entry"
HIGHSCORE = "highscore"
HOW_TO_PLAY = "how_to_play"
state = MENU

def reset_game():
    global player_rect, enemy_rect, ball_rects, player_health, score, player_fireballs, shield_zones, powerup_rects
    player_rect = player_image.get_rect(midbottom=(WIDTH // 2, HEIGHT - 50))
    enemy_rect = enemy_image.get_rect(midtop=(WIDTH // 2, 50))
    ball_rects = []
    player_fireballs = []
    powerup_rects = []
    player_health = 100
    score = 0
    shield_width = 60 * 5
    shield_height = 150 * 5
    shield_zones = [
        {"rect": pygame.Rect(enemy_rect.centerx - shield_width - 150, enemy_rect.bottom, shield_width, shield_height), "active": True, "hits": 0, "max_hits": 10},
        {"rect": pygame.Rect(enemy_rect.centerx - shield_width // 2 - 50, enemy_rect.bottom, shield_width, shield_height), "active": True, "hits": 0, "max_hits": 10},
        {"rect": pygame.Rect(enemy_rect.centerx + 50, enemy_rect.bottom, shield_width, shield_height), "active": True, "hits": 0, "max_hits": 10}
    ]

reset_game()

ball_speed = 5
ball_timer = pygame.USEREVENT + 1
burst_timer = pygame.USEREVENT + 2
powerup_timer = pygame.USEREVENT + 3
pygame.time.set_timer(ball_timer, 1000)
pygame.time.set_timer(burst_timer, 3000)
pygame.time.set_timer(powerup_timer, 10000)

player_name = ""
fireball_speed = -8
score_timer = pygame.time.get_ticks()
shield_cycle_timer = pygame.time.get_ticks()
shield_visible = True

last_fire_time = 0
fire_cooldown = 1000

invincible = False
invincible_start_time = 0
invincible_duration = 3000

while True:
    screen.fill((0, 0, 0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if state == GAME:
            if event.type == ball_timer:
                rect = ball_image.get_rect(midtop=enemy_rect.midbottom)
                ball_rects.append([rect, 0, ball_speed])
            if event.type == burst_timer:
                for i in range(20):
                    angle = math.radians(i * (360 / 20))
                    dx = math.cos(angle) * ball_speed
                    dy = math.sin(angle) * ball_speed
                    rect = ball_image.get_rect(center=enemy_rect.center)
                    ball_rects.append([rect, dx, dy])
            if event.type == powerup_timer:
                x = random.randint(50, WIDTH - 50)
                rect = powerup_image.get_rect(midtop=(x, 0))
                powerup_rects.append(rect)
        elif state == MENU:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if start_btn.collidepoint(mx, my):
                    reset_game()
                    score_timer = pygame.time.get_ticks()
                    shield_cycle_timer = pygame.time.get_ticks()
                    state = GAME
                elif high_btn.collidepoint(mx, my):
                    state = HIGHSCORE
                elif how_btn.collidepoint(mx, my):
                    state = HOW_TO_PLAY
                elif quit_btn.collidepoint(mx, my):
                    pygame.quit()
                    sys.exit()
        elif state == HIGHSCORE or state == HOW_TO_PLAY:
            if event.type == pygame.KEYDOWN:
                state = MENU
        elif state == LOSE:
            state = NAME_ENTRY
            player_name = ""
        elif state == NAME_ENTRY:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and player_name.strip():
                    save_score(player_name.strip(), score)
                    state = MENU
                elif event.key == pygame.K_BACKSPACE:
                    player_name = player_name[:-1]
                else:
                    if len(player_name) < 12 and event.unicode.isprintable():
                        player_name += event.unicode

    if state == MENU:
        screen.blit(bg_image, (0, 0))
        title = font.render("Bullet Hell", True, (255, 255, 255))
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))
        start_btn = draw_button("Start", 300, 200, 200, 50)
        high_btn = draw_button("Highscore", 300, 270, 200, 50)
        how_btn = draw_button("How to Play", 300, 340, 200, 50)
        quit_btn = draw_button("Quit", 300, 410, 200, 50)

    elif state == HOW_TO_PLAY:
        screen.blit(bg_image, (0, 0))
        title = font.render("How to Play", True, (0, 255, 255))
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))

        instructions = [
            "← → : Move left/right",
            "SPACE : Fire upward",
            "Avoid enemy balls",
            "Destroy shields to hit the enemy",
            "Collect power-ups for effects",
            "Survive as long as possible!"
        ]

        for i, line in enumerate(instructions):
            text = small_font.render(line, True, (255, 255, 255))
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 120 + i * 30))

        prompt = small_font.render("Press any key to return to menu", True, (255, 255, 255))
        screen.blit(prompt, (WIDTH // 2 - prompt.get_width() // 2, HEIGHT - 50))

    elif state == GAME:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player_rect.left > 0:
            player_rect.x -= 5
        if keys[pygame.K_RIGHT] and player_rect.right < WIDTH:
            player_rect.x += 5
        if keys[pygame.K_SPACE]:
            current_time = pygame.time.get_ticks()
            if current_time - last_fire_time >= fire_cooldown:
                fire_rect = ball_image.get_rect(midbottom=player_rect.midtop)
                player_fireballs.append(fire_rect)
                last_fire_time = current_time

        if enemy_rect.centerx < player_rect.centerx:
            enemy_rect.x += 3
        elif enemy_rect.centerx > player_rect.centerx:
            enemy_rect.x -= 3

        if pygame.time.get_ticks() - score_timer >= 1000:
            score += 1
            score_timer = pygame.time.get_ticks()

        if pygame.time.get_ticks() - shield_cycle_timer >= 10000:
            shield_visible = not shield_visible
            for shield in shield_zones:
                shield["active"] = shield_visible
                if shield_visible:
                    shield["hits"] = 0
            shield_cycle_timer = pygame.time.get_ticks()

        for ball in ball_rects:
            ball[0].x += ball[1]
            ball[0].y += ball[2]

        for fire in player_fireballs[:]:
            fire.y += fireball_speed
            if fire.bottom < 0:
                player_fireballs.remove(fire)

        for fire in player_fireballs[:]:
            for shield in shield_zones:
                if shield["active"] and fire.colliderect(shield["rect"]):
                    shield["hits"] += 1
                    player_fireballs.remove(fire)
                    if shield["hits"] >= shield["max_hits"]:
                        shield["active"] = False
                    break
            for ball in ball_rects[:]:
                if fire.colliderect(ball[0]):
                    ball_rects.remove(ball)
                    if fire in player_fireballs:
                        player_fireballs.remove(fire)
                    break

        for ball in ball_rects[:]:
            if ball[0].colliderect(player_rect):
                ball_rects.remove(ball)
                if not invincible:
                    player_health -= 10
                    if player_health <= 0:
                        state = LOSE

        for p in powerup_rects[:]:
            p.y += HEIGHT / (FPS * 3)
            if p.top > HEIGHT:
                powerup_rects.remove(p)
            elif p.colliderect(player_rect):
                invincible = True
                invincible_start_time = pygame.time.get_ticks()
                powerup_rects.remove(p)

        if invincible and pygame.time.get_ticks() - invincible_start_time >= invincible_duration:
            invincible = False

        screen.blit(bg_image, (0, 0))
        screen.blit(player_image, player_rect)
        screen.blit(enemy_image, enemy_rect)

        for shield in shield_zones:
            if shield["active"]:
                screen.blit(shield_image, shield["rect"])

        for ball in ball_rects:
            screen.blit(ball_image, ball[0])
        for fire in player_fireballs:
            screen.blit(ball_image, fire)
        for p in powerup_rects:
            screen.blit(powerup_image, p)

        pygame.draw.rect(screen, (255, 0, 0), (20, 20, 100, 10))
        pygame.draw.rect(screen, (0, 255, 0), (20, 20, player_health, 10))
        health_text = small_font.render(f"Health: {player_health}", True, (255, 255, 255))
        screen.blit(health_text, (20, 35))

        score_text = small_font.render(f"Score: {score}", True, (255, 255, 255))
        screen.blit(score_text, (WIDTH - 150, 20))

        if invincible:
            effect_text = small_font.render("INVINCIBLE!", True, (255, 255, 0))
            screen.blit(effect_text, (WIDTH // 2 - effect_text.get_width() // 2, 60))

        highscore = max([entry["score"] for entry in load_scores()] + [0])
        high_text = small_font.render(f"Highscore: {highscore}", True, (255, 255, 0))
        screen.blit(high_text, (WIDTH - high_text.get_width() - 20, 50))

    elif state == NAME_ENTRY:
        screen.blit(bg_image, (0, 0))
        prompt = font.render("You Lose! Enter your name:", True, (255, 0, 0))
        screen.blit(prompt, (WIDTH // 2 - prompt.get_width() // 2, HEIGHT // 2 - 60))
        name_text = font.render(player_name + "|", True, (255, 255, 255))
        screen.blit(name_text, (WIDTH // 2 - name_text.get_width() // 2, HEIGHT // 2))

    elif state == HIGHSCORE:
        screen.blit(bg_image, (0, 0))
        scores = load_scores()
        title = font.render("Highscores", True, (0, 255, 0))
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))
        for i, entry in enumerate(sorted(scores, key=lambda x: x["score"], reverse=True)[:10]):
            line = small_font.render(f"{i+1}. {entry['name']} - {entry['score']}", True, (255, 255, 255))
            screen.blit(line, (WIDTH // 2 - line.get_width() // 2, 100 + i * 30))
        prompt = small_font.render("Press any key to return to menu", True, (255, 255, 255))
        screen.blit(prompt, (WIDTH // 2 - prompt.get_width() // 2, HEIGHT - 50))

    pygame.display.flip()
    clock.tick(FPS)