import pygame
import sys
import pickle
import pandas as pd
import numpy as np
import random
import os
from sklearn.ensemble import RandomForestClassifier

# --- AYARLAR VE RENKLER ---
WIDTH, HEIGHT = 1000, 700
BG_COLOR = (10, 10, 18)
HUMAN_COLOR = (0, 180, 255)
AI_COLOR = (255, 140, 0)
FOOD_COLOR = (255, 40, 40)
WHITE = (255, 255, 255)
GRAY = (50, 50, 70)
HIGHLIGHT = (0, 255, 150)
BLOCK_SIZE = 22

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("🐍MimicSnake")
clock = pygame.time.Clock()
font_btn = pygame.font.SysFont("Consolas", 24, bold=True)
font_title = pygame.font.SysFont("Consolas", 50, bold=True)

# --- GLOBAL DEĞİŞKENLER ---
game_state = "MENU"
difficulty = "Medium"
SPEED_HUMAN = 5
SPEED_AI = 5
CONFIDENCE_THRESHOLD = 0.35
collected_data = []

# --- FONKSİYONLAR ---

def train_my_model():
    """Arka planda toplanan verilerle Random Forest eğitir."""
    if not os.path.exists('yilan_verisi.csv'):
        return False
    
    df = pd.read_csv('yilan_verisi.csv')
    # Özellik Mühendisliği
    df['abs_dx'] = df['dx'].abs()
    df['abs_dy'] = df['dy'].abs()
    df['manhattan'] = df['abs_dx'] + df['abs_dy']
    df['norm_dx'] = df['dx'] / (df['manhattan'] + 1)
    df['norm_dy'] = df['dy'] / (df['manhattan'] + 1)
    
    FEATURES = ['dx', 'dy', 'abs_dx', 'abs_dy', 'manhattan', 'norm_dx', 'norm_dy']
    X = df[FEATURES]
    y = df['action']
    
    model = RandomForestClassifier(n_estimators=100)
    model.fit(X, y)
    
    with open('ai_model.pkl', 'wb') as f:
        pickle.dump({'model': model, 'features': FEATURES}, f)
    return True

def draw_button(text, x, y, w, h, active, disabled=False):
    color = GRAY
    if disabled: color = (30, 30, 40)
    elif active: color = HIGHLIGHT
    
    pygame.draw.rect(screen, color, (x, y, w, h), border_radius=10)
    pygame.draw.rect(screen, WHITE if not disabled else GRAY, (x, y, w, h), 2, border_radius=10)
    
    txt_color = WHITE if not disabled else GRAY
    txt = font_btn.render(text, True, txt_color)
    screen.blit(txt, (x + (w - txt.get_width())//2, y + (h - txt.get_height())//2))
    return pygame.Rect(x, y, w, h)

def spawn_food():
    return random.randint(100, WIDTH-100), random.randint(100, HEIGHT-100)

# --- ANA DÖNGÜ ---
human_snake = []
ai_snake = []
food_pos = spawn_food()
h_score = a_score = 0
error_msg = ""
error_timer = 0

running = True
while running:
    screen.fill(BG_COLOR)
    mx, my = pygame.mouse.get_pos()
    click = False
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        if event.type == pygame.MOUSEBUTTONDOWN: click = True

    if game_state == "MENU":
        title = font_title.render("MimicSnake", True, WHITE)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 80))
        
        # Model kontrolü
        model_exists = os.path.exists('ai_model.pkl')
        
        # Butonlar
        btn_collect = draw_button("Train Me First", 350, 220, 300, 60, False)
        btn_train   = draw_button("PROCESS MODEL", 350, 300, 300, 60, False)
        btn_race    = draw_button("START RACE", 350, 380, 300, 80, False, disabled=not model_exists)
        
        # Zorluk Seçimi
        btn_easy = draw_button("EASY", 250, 500, 150, 50, difficulty == "Easy")
        btn_med  = draw_button("MED", 425, 500, 150, 50, difficulty == "Medium")
        btn_hard = draw_button("HARD", 600, 500, 150, 50, difficulty == "Hard")

        if click:
            if btn_collect.collidepoint(mx, my):
                human_snake = [[200, 350], [180, 350], [160, 350]]
                collected_data = []
                game_state = "COLLECTING"
            elif btn_train.collidepoint(mx, my):
                if train_my_model():
                    error_msg, error_timer = "MODEL TRAINED!", 120
                else:
                    error_msg, error_timer = "NO DATA FOUND!", 120
            elif btn_race.collidepoint(mx, my):
                if model_exists:
                    with open('ai_model.pkl', 'rb') as f:
                        data = pickle.load(f)
                        loaded_model, FEATURES = data['model'], data['features']
                    human_snake = [[200, 350], [180, 350]]
                    ai_snake = [[800, 350], [820, 350]]
                    h_score = a_score = 0
                    game_state = "RACING"
                else:
                    error_msg, error_timer = "TRAIN AI FIRST!", 120
            
            # Zorluk Tıklamaları
            if btn_easy.collidepoint(mx, my): difficulty, SPEED_AI, CONFIDENCE_THRESHOLD = "Easy", 4, 0.55
            if btn_med.collidepoint(mx, my):  difficulty, SPEED_AI, CONFIDENCE_THRESHOLD = "Medium", 5, 0.35
            if btn_hard.collidepoint(mx, my): difficulty, SPEED_AI, CONFIDENCE_THRESHOLD = "Hard", 6, 0.15

    elif game_state == "COLLECTING":
        # Veri Toplama Ekranı (Sadece İnsan)
        keys = pygame.key.get_pressed()
        action = "IDLE"
        dx, dy = food_pos[0] - human_snake[0][0], food_pos[1] - human_snake[0][1]
        
        move_x = move_y = 0
        if keys[pygame.K_LEFT]:  move_x, action = -SPEED_HUMAN, "LEFT"
        if keys[pygame.K_RIGHT]: move_x, action = SPEED_HUMAN, "RIGHT"
        if keys[pygame.K_UP]:    move_y, action = -SPEED_HUMAN, "UP"
        if keys[pygame.K_DOWN]:  move_y, action = SPEED_HUMAN, "DOWN"
        
        if action != "IDLE":
            collected_data.append({"dx": dx, "dy": dy, "action": action})
            new_head = [human_snake[0][0] + move_x, human_snake[0][1] + move_y]
            human_snake.insert(0, new_head)
            if pygame.Rect(new_head[0], new_head[1], 20, 20).colliderect(pygame.Rect(food_pos[0]-10, food_pos[1]-10, 20, 20)):
                food_pos = spawn_food()
            else:
                human_snake.pop()
        
        # Çizim ve Bilgi
        pygame.draw.circle(screen, FOOD_COLOR, food_pos, 10)
        for p in human_snake: pygame.draw.rect(screen, HUMAN_COLOR, (p[0], p[1], 20, 20))
        info = font_btn.render(f"COLLECTING DATA: {len(collected_data)} | PRESS ESC TO SAVE", True, WHITE)
        screen.blit(info, (20, 20))
        
        if keys[pygame.K_ESCAPE]:
            pd.DataFrame(collected_data).to_csv('yilan_verisi.csv', index=False)
            game_state = "MENU"

    elif game_state == "RACING":
        # Yarış Modu (İnsan vs AI)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]: game_state = "MENU"
        
        # İnsan Hareketi
        h_x = h_y = 0
        if keys[pygame.K_LEFT]: h_x = -SPEED_HUMAN
        if keys[pygame.K_RIGHT]: h_x = SPEED_HUMAN
        if keys[pygame.K_UP]: h_y = -SPEED_HUMAN
        if keys[pygame.K_DOWN]: h_y = SPEED_HUMAN
        
        if h_x != 0 or h_y != 0:
            human_snake.insert(0, [human_snake[0][0]+h_x, human_snake[0][1]+h_y])
            if pygame.Rect(human_snake[0][0], human_snake[0][1], 20, 20).colliderect(pygame.Rect(food_pos[0]-10, food_pos[1]-10, 20, 20)):
                h_score += 1; food_pos = spawn_food()
            else: human_snake.pop()

        # AI Hareketi
        adx, ady = food_pos[0] - ai_snake[0][0], food_pos[1] - ai_snake[0][1]
        am = abs(adx) + abs(ady)
        inp = pd.DataFrame([[adx, ady, abs(adx), abs(ady), am, adx/(am+1), ady/(am+1)]], columns=FEATURES)
        
        probs = loaded_model.predict_proba(inp)[0]
        prob_map = dict(zip(loaded_model.classes_, probs))
        
        if (1.0 - prob_map.get('IDLE', 0)) > CONFIDENCE_THRESHOLD:
            ax = SPEED_AI if adx > 0 else (-SPEED_AI if adx < 0 else 0)
            ay = SPEED_AI if ady > 0 else (-SPEED_AI if ady < 0 else 0)
            ai_snake.insert(0, [ai_snake[0][0]+ax, ai_snake[0][1]+ay])
            if pygame.Rect(ai_snake[0][0], ai_snake[0][1], 20, 20).colliderect(pygame.Rect(food_pos[0]-10, food_pos[1]-10, 20, 20)):
                a_score += 1; food_pos = spawn_food()
            else: ai_snake.pop()

        # Çizim
        pygame.draw.circle(screen, FOOD_COLOR, food_pos, 12)
        for p in human_snake: pygame.draw.rect(screen, HUMAN_COLOR, (p[0], p[1], 20, 20))
        for p in ai_snake: pygame.draw.rect(screen, AI_COLOR, (p[0], p[1], 20, 20))
        score_txt = font_btn.render(f"YOU: {h_score} | AI ({difficulty}): {a_score}", True, WHITE)
        screen.blit(score_txt, (WIDTH//2 - 150, 20))

    # Hata/Bilgi Mesajları
    if error_timer > 0:
        msg = font_btn.render(error_msg, True, HIGHLIGHT if "TRAINED" in error_msg else FOOD_COLOR)
        screen.blit(msg, (WIDTH//2 - msg.get_width()//2, HEIGHT - 50))
        error_timer -= 1

    pygame.display.flip()
    clock.tick(60)
pygame.quit()