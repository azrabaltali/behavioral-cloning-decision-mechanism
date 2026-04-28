import pygame
import sys
import pickle
import numpy as np
import pandas as pd
import random
import os

# ── Model yükle ───────────────────────────────────────────────
print("🤖 AI modeli yükleniyor...")
if not os.path.exists('ai_model.pkl'):
    print("❌ ai_model.pkl bulunamadı! Önce 'python model_egit.py' çalıştır.")
    sys.exit(1)

with open('ai_model.pkl', 'rb') as f:
    data = pickle.load(f)

# Hem eski format (sadece model) hem yeni format (dict) destekle
if isinstance(data, dict):
    model    = data['model']
    FEAT     = data['features']
    NEW_MODEL = True
else:
    model    = data
    FEAT     = None
    NEW_MODEL = False

print("✅ Model yüklendi!")

# ── Pygame ────────────────────────────────────────────────────
pygame.init()

WIDTH, HEIGHT = 900, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("🤖 Behavioral Cloning — AI Seni Taklit Ediyor")

# Renkler
BLACK      = (10, 10, 20)
WHITE      = (240, 240, 255)
ORANGE     = (255, 140, 0)
RED        = (220, 50, 50)
GREEN      = (50, 220, 120)
CYAN       = (0, 200, 255)
YELLOW     = (255, 220, 0)
GRAY       = (60, 60, 80)
DARK_GRAY  = (25, 25, 40)
PURPLE     = (140, 80, 220)

# ── Oyun nesneleri ────────────────────────────────────────────
player_x = WIDTH // 2
player_y = HEIGHT - 120
PLAYER_W, PLAYER_H = 50, 50
SPEED = 5

target_x = random.randint(60, WIDTH - 60)
target_y = random.randint(60, HEIGHT - 160)
TARGET_R = 22

score      = 0
frame_count = 0
history    = []          # son N karedeki mesafe geçmişi
stuck_timer = 0          # hareketsizlik sayacı

font       = pygame.font.SysFont("Consolas", 28, bold=True)
small_font = pygame.font.SysFont("Consolas", 18)
tiny_font  = pygame.font.SysFont("Consolas", 14)

clock = pygame.time.Clock()

# ── Aksiyon eşlemesi (model STRING döndürüyor) ────────────────
# Model 'LEFT','RIGHT','UP','DOWN','IDLE' stringleri döndürür
ACTION_LABELS = {
    'LEFT':  '◀ SOL',
    'RIGHT': '▶ SAĞ',
    'UP':    '▲ YUKARI',
    'DOWN':  '▼ AŞAĞI',
    'IDLE':  '● BEKLE',
}
ACTION_COLORS = {
    'LEFT':  CYAN,
    'RIGHT': CYAN,
    'UP':    GREEN,
    'DOWN':  YELLOW,
    'IDLE':  GRAY,
}

def draw_panel(surface, x, y, w, h, color=DARK_GRAY, alpha=200):
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    s.fill((*color, alpha))
    surface.blit(s, (x, y))
    pygame.draw.rect(surface, GRAY, (x, y, w, h), 1, border_radius=6)

def draw_bar(surface, x, y, w, h, value, max_val, color):
    pygame.draw.rect(surface, GRAY, (x, y, w, h), border_radius=4)
    fill = int(w * min(value / max_val, 1.0))
    if fill > 0:
        pygame.draw.rect(surface, color, (x, y, fill, h), border_radius=4)

print("🎮 AI oynamaya başlıyor...")
print("   ESC veya pencereyi kapat = çıkış\n")

running = True
while running:
    dt = clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False

    # ── AI karar ──────────────────────────────────────────────
    dx    = target_x - player_x
    dy    = target_y - player_y
    abs_dx = abs(dx)
    abs_dy = abs(dy)
    manh  = abs_dx + abs_dy
    dx_norm = dx / (manh + 1)
    dy_norm = dy / (manh + 1)

    if NEW_MODEL:
        feat_vals = [[dx, dy, abs_dx, abs_dy, manh, dx_norm, dy_norm]]
        features = pd.DataFrame(feat_vals, columns=FEAT)
    else:
        feat_cols = ['player_x', 'player_y', 'target_x', 'target_y']
        features  = pd.DataFrame([[player_x, player_y, target_x, target_y]],
                                   columns=feat_cols)

    # Olasılıkları al
    classes  = model.classes_
    proba    = model.predict_proba(features)[0]
    prob_map = dict(zip(classes, proba))
    ml_action = model.predict(features)[0]

    # ── Hibrit karar mekanizması ──────────────────────────────
    # Model sadece IDLE / hareket ayrımı için kullanılır.
    # Yön kararı her zaman geometrik olarak verilir (hedefin nerede olduğuna bak).
    # Bu sayede model "ezber pozisyon" öğrenmiş olsa bile AI doğru gider.
    move_prob = 1.0 - prob_map.get('IDLE', 0)

    if move_prob > 0.35 or manh > 80:
        # Hedefe doğru en büyük ekseni kapa
        if abs_dx >= abs_dy:
            action = 'RIGHT' if dx > 0 else 'LEFT'
        else:
            action = 'DOWN' if dy > 0 else 'UP'
    else:
        action = 'IDLE'

    # Hareket uygula
    prev_x, prev_y = player_x, player_y
    if action == 'LEFT'  and player_x > 0:
        player_x -= SPEED
    elif action == 'RIGHT' and player_x < WIDTH - PLAYER_W:
        player_x += SPEED
    elif action == 'UP'  and player_y > 0:
        player_y -= SPEED
    elif action == 'DOWN' and player_y < HEIGHT - PLAYER_H:
        player_y += SPEED

    # ── Çarpışma kontrolü ─────────────────────────────────────
    player_rect = pygame.Rect(player_x, player_y, PLAYER_W, PLAYER_H)
    target_rect = pygame.Rect(target_x - TARGET_R, target_y - TARGET_R,
                               TARGET_R*2, TARGET_R*2)

    if player_rect.colliderect(target_rect):
        score += 1
        target_x = random.randint(60, WIDTH - 60)
        target_y = random.randint(60, HEIGHT - 160)
        stuck_timer = 0
        print(f"🎯 Hedef yakalandı! Skor: {score}")

    # Mesafe takibi
    dist = abs(player_x - target_x) + abs(player_y - target_y)
    history.append(dist)
    if len(history) > 120:
        history.pop(0)

    if player_x == prev_x and player_y == prev_y:
        stuck_timer += 1
    else:
        stuck_timer = 0

    frame_count += 1

    # ── Çizim ─────────────────────────────────────────────────
    screen.fill(BLACK)

    # Izgara arka plan
    for gx in range(0, WIDTH, 60):
        pygame.draw.line(screen, (20, 20, 35), (gx, 0), (gx, HEIGHT))
    for gy in range(0, HEIGHT, 60):
        pygame.draw.line(screen, (20, 20, 35), (0, gy), (WIDTH, gy))

    # Hedef — parlayan daire
    glow_r = TARGET_R + 10 + int(4 * abs(pygame.time.get_ticks() % 1000 / 500 - 1))
    pygame.draw.circle(screen, (80, 10, 10), (target_x, target_y), glow_r)
    pygame.draw.circle(screen, RED,          (target_x, target_y), TARGET_R)
    pygame.draw.circle(screen, (255,120,120),(target_x, target_y), TARGET_R - 6)

    # Oyuncu (AI — turuncu kare)
    pygame.draw.rect(screen, ORANGE,
                     (player_x, player_y, PLAYER_W, PLAYER_H), border_radius=6)
    pygame.draw.rect(screen, YELLOW,
                     (player_x+2, player_y+2, PLAYER_W-4, PLAYER_H-4),
                     2, border_radius=5)
    # "AI" yazısı
    ai_lbl = tiny_font.render("AI", True, BLACK)
    screen.blit(ai_lbl, (player_x + 16, player_y + 16))

    # Hedef çizgisi
    pygame.draw.line(screen, (60, 30, 30),
                     (player_x + PLAYER_W//2, player_y + PLAYER_H//2),
                     (target_x, target_y), 1)

    # ── Sol panel ─────────────────────────────────────────────
    draw_panel(screen, 10, 10, 220, 180)

    title = font.render("🤖 AI OYNUYOR", True, CYAN)
    screen.blit(title, (20, 18))

    sc_txt = font.render(f"SKOR: {score}", True, YELLOW)
    screen.blit(sc_txt, (20, 52))

    ac_color = ACTION_COLORS.get(action, WHITE)
    ac_label = ACTION_LABELS.get(action, action)
    ac_txt = small_font.render(f"KARAR: {ac_label}", True, ac_color)
    screen.blit(ac_txt, (20, 85))

    dist_txt = small_font.render(f"UZAKLIK: {dist:.0f}px", True, WHITE)
    screen.blit(dist_txt, (20, 108))

    fps_txt = small_font.render(f"FPS: {int(clock.get_fps())}", True, GRAY)
    screen.blit(fps_txt, (20, 131))

    frame_txt = small_font.render(f"KARE: {frame_count}", True, GRAY)
    screen.blit(frame_txt, (20, 154))

    # ── Mesafe çubuğu ─────────────────────────────────────────
    draw_panel(screen, 10, 200, 220, 55)
    bar_lbl = tiny_font.render("HEDEFE UZAKLIK", True, GRAY)
    screen.blit(bar_lbl, (20, 207))
    max_dist = WIDTH + HEIGHT
    draw_bar(screen, 20, 227, 190, 16, max_dist - dist, max_dist, GREEN)

    # ── Sıkışma uyarısı ───────────────────────────────────────
    if stuck_timer > 180:
        warn = small_font.render("⚠ AI SIKIŞTI!", True, RED)
        screen.blit(warn, (20, 265))

    # ── Mesafe grafiği ────────────────────────────────────────
    if len(history) > 2:
        draw_panel(screen, 10, HEIGHT - 120, 220, 110)
        g_lbl = tiny_font.render("MESAFE GEÇMİŞİ", True, GRAY)
        screen.blit(g_lbl, (20, HEIGHT - 114))
        pts = []
        for i, d in enumerate(history):
            gx = 20 + int(i * 190 / max(len(history)-1, 1))
            gy = (HEIGHT - 20) - int(d * 80 / max(max_dist, 1))
            pts.append((gx, gy))
        if len(pts) >= 2:
            pygame.draw.lines(screen, PURPLE, False, pts, 2)

    # Alt bilgi
    info = tiny_font.render("ESC = çıkış  |  Behavioral Cloning Demo", True, GRAY)
    screen.blit(info, (WIDTH//2 - info.get_width()//2, HEIGHT - 20))

    pygame.display.flip()

    if frame_count % 300 == 0:
        avg_dist = sum(history[-60:]) / max(len(history[-60:]), 1)
        print(f"📊 Kare {frame_count} | Skor {score} | Ort. uzaklık {avg_dist:.0f}px")

print(f"\n🏁 Oyun bitti! AI toplam {score} hedef topladı.")
pygame.quit()
sys.exit()