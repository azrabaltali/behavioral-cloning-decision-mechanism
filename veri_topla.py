import pygame
import sys
import csv
import random
from datetime import datetime

pygame.init()

WIDTH, HEIGHT = 900, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("🎮 VERİ TOPLANIYOR — Ok tuşları ile oyna!")

# Renkler
BLACK     = (10, 10, 20)
WHITE     = (240, 240, 255)
BLUE      = (50, 130, 255)
BLUE_LT   = (100, 170, 255)
RED       = (220, 50, 50)
GREEN     = (50, 220, 120)
YELLOW    = (255, 220, 0)
GRAY      = (60, 60, 80)
DARK_GRAY = (25, 25, 40)
CYAN      = (0, 200, 255)

player_x   = WIDTH // 2
player_y   = HEIGHT - 120
PLAYER_W   = 50
PLAYER_H   = 50
SPEED      = 5

target_x   = random.randint(60, WIDTH - 60)
target_y   = random.randint(60, HEIGHT - 160)
TARGET_R   = 22

score      = 0
font       = pygame.font.SysFont("Consolas", 28, bold=True)
small_font = pygame.font.SysFont("Consolas", 18)
tiny_font  = pygame.font.SysFont("Consolas", 14)

# CSV dosyası
filename = f"veri_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
print(f"📝 Veriler '{filename}' dosyasına kaydediliyor")
print("   Ok tuşları ile mavi kareyi kırmızı daireye götür!")
print("   ESC = kaydet & çık\n")

with open(filename, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['player_x', 'player_y', 'target_x', 'target_y',
                     'left', 'right', 'up', 'down', 'score'])

clock        = pygame.time.Clock()
running      = True
record_count = 0
move_count   = 0

def draw_panel(surface, x, y, w, h):
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    s.fill((25, 25, 40, 200))
    surface.blit(s, (x, y))
    pygame.draw.rect(surface, GRAY, (x, y, w, h), 1, border_radius=6)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False

    keys = pygame.key.get_pressed()

    left = right = up = down = 0

    if keys[pygame.K_LEFT]  and player_x > 0:
        player_x -= SPEED;  left  = 1
    if keys[pygame.K_RIGHT] and player_x < WIDTH  - PLAYER_W:
        player_x += SPEED;  right = 1
    if keys[pygame.K_UP]    and player_y > 0:
        player_y -= SPEED;  up    = 1
    if keys[pygame.K_DOWN]  and player_y < HEIGHT - PLAYER_H:
        player_y += SPEED;  down  = 1

    if any([left, right, up, down]):
        move_count += 1

    # Çarpışma
    player_rect = pygame.Rect(player_x, player_y, PLAYER_W, PLAYER_H)
    target_rect = pygame.Rect(target_x - TARGET_R, target_y - TARGET_R,
                               TARGET_R*2, TARGET_R*2)
    if player_rect.colliderect(target_rect):
        score   += 1
        target_x = random.randint(60, WIDTH - 60)
        target_y = random.randint(60, HEIGHT - 160)

    # Kaydet
    with open(filename, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([player_x, player_y, target_x, target_y,
                         left, right, up, down, score])
        record_count += 1

    # ── Çizim ─────────────────────────────────────────────────
    screen.fill(BLACK)

    # Izgara
    for gx in range(0, WIDTH, 60):
        pygame.draw.line(screen, (20, 20, 35), (gx, 0), (gx, HEIGHT))
    for gy in range(0, HEIGHT, 60):
        pygame.draw.line(screen, (20, 20, 35), (0, gy), (WIDTH, gy))

    # Hedef
    glow_r = TARGET_R + 8 + int(4 * abs(pygame.time.get_ticks() % 1000 / 500 - 1))
    pygame.draw.circle(screen, (80, 10, 10), (target_x, target_y), glow_r)
    pygame.draw.circle(screen, RED,          (target_x, target_y), TARGET_R)
    pygame.draw.circle(screen, (255,120,120),(target_x, target_y), TARGET_R - 6)

    # Oyuncu (mavi kare — insan)
    pygame.draw.rect(screen, BLUE,
                     (player_x, player_y, PLAYER_W, PLAYER_H), border_radius=6)
    pygame.draw.rect(screen, BLUE_LT,
                     (player_x+2, player_y+2, PLAYER_W-4, PLAYER_H-4),
                     2, border_radius=5)
    lbl = tiny_font.render("SEN", True, WHITE)
    screen.blit(lbl, (player_x + 10, player_y + 16))

    # Hedef çizgisi
    pygame.draw.line(screen, (60, 30, 30),
                     (player_x + PLAYER_W//2, player_y + PLAYER_H//2),
                     (target_x, target_y), 1)

    # ── Sol panel ─────────────────────────────────────────────
    draw_panel(screen, 10, 10, 230, 155)

    title = font.render("🎮 VERİ TOPLANIYOR", True, CYAN)
    screen.blit(title, (20, 18))

    sc_txt = font.render(f"SKOR: {score}", True, YELLOW)
    screen.blit(sc_txt, (20, 52))

    rec_txt = small_font.render(f"KAYIT: {record_count}", True, WHITE)
    screen.blit(rec_txt, (20, 82))

    mov_pct = (move_count / max(record_count, 1)) * 100
    mov_txt = small_font.render(f"HAREKET: %{mov_pct:.0f}", True, GREEN)
    screen.blit(mov_txt, (20, 105))

    dist    = abs(player_x - target_x) + abs(player_y - target_y)
    d_txt   = small_font.render(f"UZAKLIK: {dist}px", True, WHITE)
    screen.blit(d_txt, (20, 128))

    # Tuş göstergesi
    draw_panel(screen, 10, HEIGHT - 100, 230, 90)
    keys_lbl = tiny_font.render("BASILI TUŞLAR:", True, GRAY)
    screen.blit(keys_lbl, (20, HEIGHT - 93))

    for i, (lbl_txt, val) in enumerate([("◀ SOL", left), ("▶ SAĞ", right),
                                         ("▲ YUK", up),   ("▼ AŞA", down)]):
        color = GREEN if val else GRAY
        t = small_font.render(lbl_txt, True, color)
        screen.blit(t, (20 + i * 55, HEIGHT - 68))

    # Alt bilgi
    info = tiny_font.render("ESC = kaydet & çık  |  Kırmızı daireye dokunmaya çalış!", True, GRAY)
    screen.blit(info, (WIDTH//2 - info.get_width()//2, HEIGHT - 18))

    pygame.display.flip()
    clock.tick(60)

print(f"\n✅ {record_count} hamle kaydedildi: {filename}")
print(f"   Skor: {score} | Hareket oranı: %{(move_count/max(record_count,1))*100:.1f}")
pygame.quit()
sys.exit()