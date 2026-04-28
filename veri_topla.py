import pygame
import sys
import csv
import random
from datetime import datetime

pygame.init()

WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("VERI TOPLANIYOR - Oynayarak veri topla")

WHITE = (255,255,255)
BLUE = (0,0,255)
RED = (255,0,0)
GREEN = (0,255,0)
BLACK = (0,0,0)
YELLOW = (255,255,0)

player_x = WIDTH // 2
player_y = HEIGHT - 100
player_width = 50
player_height = 50
player_speed = 5

target_x = random.randint(50, WIDTH - 50)
target_y = random.randint(50, HEIGHT - 200)
target_radius = 20

score = 0
font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 24)

# CSV dosyası oluştur
filename = f"veri_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
print(f"📝 Veriler {filename} dosyasina kaydedilecek")

with open(filename, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['player_x', 'player_y', 'target_x', 'target_y', 'left', 'right', 'up', 'down', 'score'])

clock = pygame.time.Clock()
running = True
record_count = 0

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    keys = pygame.key.get_pressed()
    
    left = right = up = down = 0
    
    if keys[pygame.K_LEFT] and player_x > 0:
        player_x -= player_speed
        left = 1
    if keys[pygame.K_RIGHT] and player_x < WIDTH - player_width:
        player_x += player_speed
        right = 1
    if keys[pygame.K_UP] and player_y > 0:
        player_y -= player_speed
        up = 1
    if keys[pygame.K_DOWN] and player_y < HEIGHT - player_height:
        player_y += player_speed
        down = 1
    
    player_rect = pygame.Rect(player_x, player_y, player_width, player_height)
    target_rect = pygame.Rect(target_x - target_radius, target_y - target_radius, target_radius*2, target_radius*2)
    
    if player_rect.colliderect(target_rect):
        score += 1
        target_x = random.randint(50, WIDTH - 50)
        target_y = random.randint(50, HEIGHT - 200)
    
    # Veriyi kaydet
    with open(filename, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([player_x, player_y, target_x, target_y, left, right, up, down, score])
        record_count += 1
    
    screen.fill(BLACK)
    pygame.draw.rect(screen, BLUE, (player_x, player_y, player_width, player_height))
    pygame.draw.circle(screen, RED, (target_x, target_y), target_radius)
    
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))
    
    record_text = small_font.render(f"Kayit: {record_count}", True, YELLOW)
    screen.blit(record_text, (10, 50))
    
    info = small_font.render("Hedefe dokun! Veri toplaniyor...", True, GREEN)
    screen.blit(info, (10, HEIGHT - 30))
    
    pygame.display.flip()
    clock.tick(60)

print(f"\n✅ {record_count} hamle kaydedildi: {filename}")
pygame.quit()
sys.exit()