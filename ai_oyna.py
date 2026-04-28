import pygame
import sys
import pickle
import numpy as np
import random

# Modeli yükle
print("🤖 AI modeli yükleniyor...")
with open('ai_model.pkl', 'rb') as f:
    model = pickle.load(f)
print("✅ Model yüklendi!")

pygame.init()

WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AI OYNUYOR - Behavioral Cloning")

# Renkler
WHITE = (255, 255, 255)
ORANGE = (255, 165, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)

# Oyuncu
player_x = WIDTH // 2
player_y = HEIGHT - 100
player_width = 50
player_height = 50
player_speed = 5

# Hedef
target_x = random.randint(50, WIDTH - 50)
target_y = random.randint(50, HEIGHT - 200)
target_radius = 20

# Skor
score = 0
font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 24)

# Aksiyon isimleri
action_names = {
    0: "SOL", 
    1: "SAG", 
    2: "YUKARI", 
    3: "ASAGI", 
    4: "BEKLE"
}

# Aksiyonların tuşları ve hareketleri
action_keys = {
    0: pygame.K_LEFT,
    1: pygame.K_RIGHT,
    2: pygame.K_UP,
    3: pygame.K_DOWN,
    4: None
}

clock = pygame.time.Clock()
running = True
frame_count = 0
last_target_time = pygame.time.get_ticks()

print("🎮 AI oynamaya başlıyor...")

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # AI karar ver
    state = np.array([[player_x, player_y, target_x, target_y]])
    action = model.predict(state)[0]
    
    # AI'ın kararına göre hareket et
    if action == 0 and player_x > 0:
        player_x -= player_speed
    elif action == 1 and player_x < WIDTH - player_width:
        player_x += player_speed
    elif action == 2 and player_y > 0:
        player_y -= player_speed
    elif action == 3 and player_y < HEIGHT - player_height:
        player_y += player_speed
    
    # Çarpışma kontrolü (AI hedefe dokundu mu?)
    player_rect = pygame.Rect(player_x, player_y, player_width, player_height)
    target_rect = pygame.Rect(target_x - target_radius, target_y - target_radius, 
                               target_radius * 2, target_radius * 2)
    
    if player_rect.colliderect(target_rect):
        score += 1
        target_x = random.randint(50, WIDTH - 50)
        target_y = random.randint(50, HEIGHT - 200)
        print(f"🎯 Hedef yakalandı! Skor: {score}")
    
    # Ekranı temizle
    screen.fill(BLACK)
    
    # Oyuncuyu çiz (turuncu kare)
    pygame.draw.rect(screen, ORANGE, (player_x, player_y, player_width, player_height))
    
    # Hedefi çiz (kırmızı daire)
    pygame.draw.circle(screen, RED, (target_x, target_y), target_radius)
    
    # Bilgileri göster
    score_text = font.render(f"AI Skor: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))
    
    action_text = small_font.render(f"AI Karari: {action_names[action]}", True, GREEN)
    screen.blit(action_text, (10, 50))
    
    # Hedefe olan mesafeyi göster
    distance = abs(player_x - target_x) + abs(player_y - target_y)
    distance_text = small_font.render(f"Hedefe Uzaklik: {distance}", True, YELLOW)
    screen.blit(distance_text, (10, 80))
    
    info_text = small_font.render("AI seni taklit ediyor!", True, WHITE)
    screen.blit(info_text, (10, HEIGHT - 30))
    
    # FPS'i göster
    fps_text = small_font.render(f"FPS: {int(clock.get_fps())}", True, WHITE)
    screen.blit(fps_text, (WIDTH - 80, 10))
    
    # Ekranı güncelle
    pygame.display.flip()
    clock.tick(60)
    
    frame_count += 1
    if frame_count % 300 == 0:
        print(f"📊 AI {frame_count} kare oynadi. Toplam skor: {score}")

print(f"\n🏁 Oyun bitti! AI toplam {score} hedef topladi.")
pygame.quit()
sys.exit()