import pygame
import sys
import pickle
import numpy as np
import pandas as pd
import random
import os

# ── Model ve Özellik Yükleme ──────────────────────────────────
if not os.path.exists('ai_model.pkl'):
    print("❌ ai_model.pkl bulunamadı!")
    sys.exit(1)

with open('ai_model.pkl', 'rb') as f:
    data = pickle.load(f)
    model = data['model']
    FEATURES = data['features']

# ── Pygame Başlat ─────────────────────────────────────────────
pygame.init()
WIDTH, HEIGHT = 1000, 700 # Biraz daha geniş alan
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("⚔️ Human vs AI: The Race")

# Renk Paleti
DARK_BG   = (15, 15, 25)
HUMAN_CLR = (50, 150, 255)  # Mavi (Sen)
AI_CLR    = (255, 150, 50)  # Turuncu (AI)
TARGET_CLR = (255, 50, 80)
WHITE     = (240, 240, 255)
GRAY      = (50, 50, 70)

# ── Nesneler ──────────────────────────────────────────────────
# İnsan (Sen)
h_x, h_y = 100, HEIGHT // 2
# AI (Klonun)
a_x, a_y = WIDTH - 150, HEIGHT // 2

SIZE = 45
SPEED = 5

target_x = random.randint(100, WIDTH - 100)
target_y = random.randint(100, HEIGHT - 100)
TARGET_R = 20

h_score = 0
a_score = 0
clock = pygame.time.Clock()
font = pygame.font.SysFont("Consolas", 24, bold=True)

def spawn_target():
    return random.randint(100, WIDTH - 100), random.randint(100, HEIGHT - 100)

print("🚀 Yarış başlıyor! Hedefe ilk ulaşan puanı alır.")

running = True
while running:
    screen.fill(DARK_BG)
    dt = clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False

    # 1. İNSAN HAREKETİ
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and h_x > 0: h_x -= SPEED
    if keys[pygame.K_RIGHT] and h_x < WIDTH - SIZE: h_x += SPEED
    if keys[pygame.K_UP] and h_y > 0: h_y -= SPEED
    if keys[pygame.K_DOWN] and h_y < HEIGHT - SIZE: h_y += SPEED

    # 2. AI HAREKETİ (Senin modelin karar veriyor)
    dx = target_x - a_x
    dy = target_y - a_y
    abs_dx, abs_dy = abs(dx), abs(dy)
    manh = abs_dx + abs_dy
    
    # Modelin beklediği özellik setini oluştur
    feat_vals = [[dx, dy, abs_dx, abs_dy, manh, dx/(manh+1), dy/(manh+1)]]
    features_df = pd.DataFrame(feat_vals, columns=FEATURES)
    
    # Tahmin al
    prob = model.predict_proba(features_df)[0]
    prob_map = dict(zip(model.classes_, prob))
    move_prob = 1.0 - prob_map.get('IDLE', 0)

    # Karar Mekanizması (Hybrid)
    if move_prob > 0.30 or manh > 50:
        if abs_dx >= abs_dy:
            a_action = 'RIGHT' if dx > 0 else 'LEFT'
        else:
            a_action = 'DOWN' if dy > 0 else 'UP'
    else:
        a_action = 'IDLE'

    # AI Hareket Uygula
    if a_action == 'LEFT' and a_x > 0: a_x -= SPEED
    if a_action == 'RIGHT' and a_x < WIDTH - SIZE: a_x += SPEED
    if a_action == 'UP' and a_y > 0: a_y -= SPEED
    if a_action == 'DOWN' and a_y < HEIGHT - SIZE: a_y += SPEED

    # 3. ÇARPIŞMA VE PUANLAMA
    target_rect = pygame.Rect(target_x-TARGET_R, target_y-TARGET_R, TARGET_R*2, TARGET_R*2)
    h_rect = pygame.Rect(h_x, h_y, SIZE, SIZE)
    a_rect = pygame.Rect(a_x, a_y, SIZE, SIZE)

    if h_rect.colliderect(target_rect):
        h_score += 1
        target_x, target_y = spawn_target()
    elif a_rect.colliderect(target_rect):
        a_score += 1
        target_x, target_y = spawn_target()

    # 4. GÖRSELLEŞTİRME (UI)
    # Izgara
    for x in range(0, WIDTH, 50): pygame.draw.line(screen, (30,30,45), (x,0), (x,HEIGHT))
    for y in range(0, HEIGHT, 50): pygame.draw.line(screen, (30,30,45), (0,y), (WIDTH,y))

    # Karakterler
    pygame.draw.rect(screen, HUMAN_CLR, (h_x, h_y, SIZE, SIZE), border_radius=8)
    pygame.draw.rect(screen, AI_CLR, (a_x, a_y, SIZE, SIZE), border_radius=8)
    pygame.draw.circle(screen, TARGET_CLR, (target_x, target_y), TARGET_R)

    # Skor Tablosu
    s_bg = pygame.Surface((300, 100), pygame.SRCALPHA)
    s_bg.fill((0,0,0,150))
    screen.blit(s_bg, (WIDTH//2 - 150, 10))
    
    h_txt = font.render(f"HUMAN: {h_score}", True, HUMAN_CLR)
    a_txt = font.render(f"AI CLONE: {a_score}", True, AI_CLR)
    screen.blit(h_txt, (WIDTH//2 - 130, 25))
    screen.blit(a_txt, (WIDTH//2 - 130, 60))

    pygame.display.flip()

pygame.quit()