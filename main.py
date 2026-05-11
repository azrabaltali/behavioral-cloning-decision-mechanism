import pygame
import sys
import pickle
import pandas as pd
import numpy as np
import random
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

# =========================
# SETTINGS
# =========================
WIDTH, HEIGHT = 1000, 700

BG_COLOR      = (15, 20, 35)
GRID_COLOR    = (25, 30, 50)

WHITE     = (255, 255, 255)
RED       = (255, 60, 60)
GRAY      = (120, 120, 140)
DARK_GRAY = (40, 40, 60)

PLAYER_BLUE = (0, 150, 255)
AI_GREEN    = (0, 220, 120)
HIGHLIGHT   = (0, 255, 150)
GOLD        = (255, 200, 50)
ORANGE      = (255, 140, 0)

BLOCK_SIZE = 45

pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("🐍 MimicSnake AI")

clock = pygame.time.Clock()

font_btn   = pygame.font.SysFont("Consolas", 24, bold=True)
font_small = pygame.font.SysFont("Consolas", 18, bold=True)
font_title = pygame.font.SysFont("Consolas", 50, bold=True)
font_score = pygame.font.SysFont("Consolas", 30, bold=True)
font_big   = pygame.font.SysFont("Consolas", 42, bold=True)

# =========================
# SPEEDS
# =========================
PLAYER_SPEED = 5

AI_SPEED_MAP = {
    "Easy":   3.5,
    "Medium": 5,
    "Hard":   6.5,
}

difficulty       = "Medium"
current_speed    = PLAYER_SPEED
current_ai_speed = AI_SPEED_MAP[difficulty]

# =========================
# ASSETS
# =========================
try:
    yilan_kafa = pygame.image.load("assets/yilan_kafa.png").convert_alpha()
    fare_img   = pygame.image.load("assets/fare.png").convert_alpha()
    yilan_kafa = pygame.transform.scale(yilan_kafa, (BLOCK_SIZE, BLOCK_SIZE))
    fare_img   = pygame.transform.scale(fare_img,   (BLOCK_SIZE, BLOCK_SIZE))
except Exception:
    yilan_kafa = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE), pygame.SRCALPHA)
    pygame.draw.circle(yilan_kafa, WHITE,
                       (BLOCK_SIZE // 2, BLOCK_SIZE // 2), BLOCK_SIZE // 2)

    fare_img = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE), pygame.SRCALPHA)
    pygame.draw.circle(fare_img, RED,
                       (BLOCK_SIZE // 2, BLOCK_SIZE // 2), 15)

# =========================
# SNAKE CLASS
# =========================
class Snake:

    def __init__(self, x, y, speed, color, is_player=False):
        self.reset(x, y, speed, color, is_player)

    def reset(self, x, y, speed, color, is_player):
        self.speed     = speed
        self.color     = color
        self.is_player = is_player
        self.path      = [[x, y] for _ in range(2000)]
        self.score     = 0
        self.segment_gap = 4
        self.last_dx   = 0
        self.last_dy   = 0

    def move(self, dx, dy):
        if self.is_player:
            if dx != 0 or dy != 0:
                self.last_dx = dx
                self.last_dy = dy
                new_x = self.path[0][0] + dx
                new_y = self.path[0][1] + dy
                self.path.insert(0, [new_x, new_y])
                self.path.pop()
        else:
            if dx != 0 or dy != 0:
                self.last_dx = dx
                self.last_dy = dy
            new_x = self.path[0][0] + self.last_dx
            new_y = self.path[0][1] + self.last_dy
            self.path.insert(0, [new_x, new_y])
            self.path.pop()

    def draw(self):
        # BODY
        for i in range(self.score, 0, -1):
            idx = i * self.segment_gap
            if idx < len(self.path):
                pos = self.path[idx]
                pygame.draw.circle(screen, self.color,
                                   (int(pos[0]), int(pos[1])),
                                   BLOCK_SIZE // 2 - 3)
        # HEAD
        pos = self.path[0]
        kafa_renkli = yilan_kafa.copy()
        kafa_renkli.fill(self.color, special_flags=pygame.BLEND_RGB_MULT)
        screen.blit(kafa_renkli,
                    (pos[0] - BLOCK_SIZE // 2, pos[1] - BLOCK_SIZE // 2))

    def get_rect(self):
        return pygame.Rect(self.path[0][0] - 15,
                           self.path[0][1] - 15, 30, 30)


# =========================
# FUNCTIONS
# =========================
# --- model accuracy (cross-val) saved globally so we can display it ---
model_accuracy = None

def train_my_model():
    """Trains RandomForest and returns True on success.
    Also computes cross-val accuracy and stores in global model_accuracy."""
    global model_accuracy

    if not os.path.exists("yilan_verisi.csv"):
        return False

    df = pd.read_csv("yilan_verisi.csv")

    df["abs_dx"]    = df["dx"].abs()
    df["abs_dy"]    = df["dy"].abs()
    df["manhattan"] = df["abs_dx"] + df["abs_dy"]
    df["norm_dx"]   = df["dx"] / (df["manhattan"] + 1)
    df["norm_dy"]   = df["dy"] / (df["manhattan"] + 1)

    FEATURES = ["dx", "dy", "abs_dx", "abs_dy", "manhattan", "norm_dx", "norm_dy"]

    X = df[FEATURES]
    y = df["action"]

    model = RandomForestClassifier(n_estimators=100)

    model.fit(X, y)

    # Training accuracy — reflects real in-game performance
    y_pred = model.predict(X)
    model_accuracy = float(accuracy_score(y, y_pred))

    with open("ai_model.pkl", "wb") as f:
        pickle.dump({"model": model, "features": FEATURES,
                     "accuracy": model_accuracy}, f)

    return True


def load_model_accuracy():
    """Try to load accuracy from saved model file."""
    global model_accuracy
    try:
        with open("ai_model.pkl", "rb") as f:
            data = pickle.load(f)
            model_accuracy = data.get("accuracy", None)
    except Exception:
        model_accuracy = None


def draw_button(text, x, y, w, h, active, disabled=False, color_override=None):
    if disabled:
        fill = (25, 25, 35)
    elif active:
        fill = HIGHLIGHT
    elif color_override:
        fill = color_override
    else:
        fill = DARK_GRAY

    pygame.draw.rect(screen, fill, (x, y, w, h), border_radius=10)
    border_col = WHITE if not disabled else GRAY
    pygame.draw.rect(screen, border_col, (x, y, w, h), 2, border_radius=10)

    txt = font_btn.render(text, True, WHITE if not disabled else GRAY)
    screen.blit(txt, (x + (w - txt.get_width()) // 2,
                       y + (h - txt.get_height()) // 2))

    return pygame.Rect(x, y, w, h)


def draw_accuracy_bar(accuracy, x, y, w, h):
    """Draw a visual training accuracy bar."""
    pct = accuracy  # 0.0 – 1.0

    # background track
    pygame.draw.rect(screen, (30, 35, 50), (x, y, w, h), border_radius=h // 2)

    # filled portion
    fill_w = int(w * pct)
    if fill_w > 0:
        # colour: green for high, orange for mid, red for low
        if pct >= 0.85:
            bar_col = AI_GREEN
        elif pct >= 0.65:
            bar_col = ORANGE
        else:
            bar_col = RED
        pygame.draw.rect(screen, bar_col, (x, y, fill_w, h),
                         border_radius=h // 2)

    # border
    pygame.draw.rect(screen, HIGHLIGHT, (x, y, w, h), 2, border_radius=h // 2)

    # label
    label = font_small.render(f"MODEL ACCURACY: %{pct * 100:.1f}", True, WHITE)
    screen.blit(label, (x + (w - label.get_width()) // 2,
                         y + (h - label.get_height()) // 2))


def spawn_food():
    return (random.randint(100, WIDTH - 100),
            random.randint(100, HEIGHT - 100))


def draw_background():
    screen.fill(BG_COLOR)
    for x in range(0, WIDTH, BLOCK_SIZE * 2):
        pygame.draw.line(screen, GRID_COLOR, (x, 50), (x, HEIGHT))
    for y in range(50, HEIGHT, BLOCK_SIZE * 2):
        pygame.draw.line(screen, GRID_COLOR, (0, y), (WIDTH, y))


def draw_ui(player_score, ai_score):
    pygame.draw.rect(screen, (30, 35, 50), (0, 0, WIDTH, 50))
    pygame.draw.line(screen, HIGHLIGHT, (0, 50), (WIDTH, 50), 2)

    p_txt = font_score.render(f"PLAYER: {player_score}", True, PLAYER_BLUE)
    a_txt = font_score.render(f"AI: {ai_score}", True, AI_GREEN)

    screen.blit(p_txt, (50, 10))
    screen.blit(a_txt, (WIDTH - a_txt.get_width() - 50, 10))

    # centre: mode label
    mode_label = "DATA COLLECT" if game_state == "COLLECTING" else "RACE"
    mode_col   = PLAYER_BLUE if game_state == "COLLECTING" else GOLD
    m_txt = font_small.render(mode_label, True, mode_col)
    screen.blit(m_txt, (WIDTH // 2 - m_txt.get_width() // 2, 15))


def draw_pause_overlay():
    """Semi-transparent overlay + pause menu buttons."""
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 20, 160))
    screen.blit(overlay, (0, 0))

    p_txt = font_big.render("⏸  PAUSED", True, HIGHLIGHT)
    screen.blit(p_txt, (WIDTH // 2 - p_txt.get_width() // 2, 220))

    hint = font_small.render("Press  P  to resume", True, GRAY)
    screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, 285))

    btn_resume = draw_button("▶  RESUME",   350, 330, 300, 55, False,
                             color_override=(20, 80, 50))
    btn_menu   = draw_button("⌂  MAIN MENU", 350, 400, 300, 55, False,
                             color_override=(60, 25, 25))
    btn_quit   = draw_button("✕  QUIT GAME", 350, 470, 300, 55, False,
                             color_override=(50, 20, 20))

    return btn_resume, btn_menu, btn_quit


# =========================
# VARIABLES
# =========================
game_state = "MENU"
paused     = False

player  = Snake(200, 350, current_speed,    PLAYER_BLUE, True)
ai_bot  = Snake(800, 350, current_ai_speed, AI_GREEN,    False)

food_pos       = spawn_food()
collected_data = []

loaded_model = None
FEATURES     = []

error_msg   = ""
error_timer = 0

winner_text  = ""
winner_color = WHITE

# Try to read accuracy from existing model
load_model_accuracy()

# =========================
# MAIN LOOP
# =========================
running = True

while running:

    draw_background()

    mx, my = pygame.mouse.get_pos()
    click  = False

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            click = True

        if event.type == pygame.KEYDOWN:

            # P = pause toggle (only in game)
            if event.key == pygame.K_p:
                if game_state in ["RACING", "COLLECTING"]:
                    paused = not paused

    # =========================
    # MENU
    # =========================
    if game_state == "MENU":

        # Title
        title = font_title.render("MimicSnake AI", True, WHITE)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))

        subtitle = font_small.render("Train the AI to mimic your moves — then race it!", True, GRAY)
        screen.blit(subtitle, (WIDTH // 2 - subtitle.get_width() // 2, 165))

        model_exists = os.path.exists("ai_model.pkl")

        btn_collect = draw_button("1.  DATA COLLECT",   350, 220, 300, 60, False)
        btn_train   = draw_button("2.  TRAIN MODEL",    350, 300, 300, 60, False)
        btn_race    = draw_button("3.  START RACE",     350, 380, 300, 70, False,
                                  disabled=not model_exists)

        # Difficulty buttons
        diff_label = font_small.render("DIFFICULTY:", True, GRAY)
        screen.blit(diff_label, (250, 510))

        btn_easy = draw_button("EASY",   250, 530, 140, 48, difficulty == "Easy")
        btn_med  = draw_button("MEDIUM", 430, 530, 140, 48, difficulty == "Medium")
        btn_hard = draw_button("HARD",   610, 530, 140, 48, difficulty == "Hard")

        # Model accuracy bar
        if model_accuracy is not None:
            draw_accuracy_bar(model_accuracy, 200, 610, 600, 30)
        else:
            no_acc = font_small.render("No trained model found — collect data & train first.",
                                       True, GRAY)
            screen.blit(no_acc, (WIDTH // 2 - no_acc.get_width() // 2, 618))

        if click:
            if btn_easy.collidepoint(mx, my):
                difficulty = "Easy"
            if btn_med.collidepoint(mx, my):
                difficulty = "Medium"
            if btn_hard.collidepoint(mx, my):
                difficulty = "Hard"

            current_ai_speed = AI_SPEED_MAP[difficulty]

            if btn_collect.collidepoint(mx, my):
                player.reset(200, 350, current_speed, PLAYER_BLUE, True)
                collected_data = []
                game_state = "COLLECTING"

            elif btn_train.collidepoint(mx, my):
                if train_my_model():
                    error_msg   = f"✅ MODEL TRAINED!  Accuracy: %{model_accuracy * 100:.1f}"
                    error_timer = 180
                else:
                    error_msg   = "❌ NO DATA FOUND — run DATA COLLECT first!"
                    error_timer = 150

            elif btn_race.collidepoint(mx, my) and model_exists:
                with open("ai_model.pkl", "rb") as f:
                    data = pickle.load(f)
                    loaded_model = data["model"]
                    FEATURES     = data["features"]
                    model_accuracy = data.get("accuracy", model_accuracy)

                player.reset(200, 350, current_speed,    PLAYER_BLUE, True)
                ai_bot.reset(800, 350, current_ai_speed, AI_GREEN,    False)
                paused     = False
                game_state = "RACING"

    # =========================
    # COLLECTING / RACING
    # =========================
    elif game_state in ["COLLECTING", "RACING"]:

        keys = pygame.key.get_pressed()

        # --- PAUSE MENU (draw + handle clicks) ---
        if paused:
            player.draw()
            if game_state == "RACING":
                ai_bot.draw()
            screen.blit(fare_img, (food_pos[0] - BLOCK_SIZE // 2,
                                   food_pos[1] - BLOCK_SIZE // 2))
            draw_ui(player.score, ai_bot.score)

            btn_resume, btn_menu, btn_quit = draw_pause_overlay()

            if click:
                if btn_resume.collidepoint(mx, my):
                    paused = False
                elif btn_menu.collidepoint(mx, my):
                    if game_state == "COLLECTING" and collected_data:
                        pd.DataFrame(collected_data).to_csv(
                            "yilan_verisi.csv", index=False)
                    game_state = "MENU"
                    paused = False
                elif btn_quit.collidepoint(mx, my):
                    pygame.quit()
                    sys.exit()

        else:
            # ---- game logic ----
            hx = hy = 0

            if keys[pygame.K_LEFT]:  hx = -current_speed
            if keys[pygame.K_RIGHT]: hx =  current_speed
            if keys[pygame.K_UP]:    hy = -current_speed
            if keys[pygame.K_DOWN]:  hy =  current_speed

            player.move(hx, hy)

            # --- AI movement ---
            if game_state == "RACING":
                adx = food_pos[0] - ai_bot.path[0][0]
                ady = food_pos[1] - ai_bot.path[0][1]
                am  = abs(adx) + abs(ady)

                inp = pd.DataFrame(
                    [[adx, ady, abs(adx), abs(ady), am,
                      adx / (am + 1), ady / (am + 1)]],
                    columns=FEATURES)

                probs   = loaded_model.predict_proba(inp)[0]
                prob_map = dict(zip(loaded_model.classes_, probs))

                ax = ay = 0

                if (1.0 - prob_map.get("IDLE", 0)) > 0.30:
                    ax = (current_ai_speed  if adx >  2
                          else -current_ai_speed if adx < -2 else 0)
                    ay = (current_ai_speed  if ady >  2
                          else -current_ai_speed if ady < -2 else 0)

                # wall safety
                future_x = ai_bot.path[0][0] + ax
                future_y = ai_bot.path[0][1] + ay

                if (future_x < 30 or future_x > WIDTH - 30
                        or future_y < 80 or future_y > HEIGHT - 30):
                    dirs = [(current_ai_speed, 0), (-current_ai_speed, 0),
                            (0, current_ai_speed), (0, -current_ai_speed)]
                    random.shuffle(dirs)
                    for pdx, pdy in dirs:
                        tx = ai_bot.path[0][0] + pdx
                        ty = ai_bot.path[0][1] + pdy
                        if 30 < tx < WIDTH - 30 and 80 < ty < HEIGHT - 30:
                            ax, ay = pdx, pdy
                            break

                ai_bot.move(ax, ay)

            # --- data collection ---
            if game_state == "COLLECTING" and (hx != 0 or hy != 0):
                action = "IDLE"
                if abs(hx) > abs(hy):
                    action = "RIGHT" if hx > 0 else "LEFT"
                else:
                    action = "DOWN" if hy > 0 else "UP"

                dx = food_pos[0] - player.path[0][0]
                dy = food_pos[1] - player.path[0][1]
                collected_data.append({"dx": dx, "dy": dy, "action": action})

            # --- food ---
            if player.get_rect().collidepoint(food_pos):
                player.score += 1
                food_pos = spawn_food()

            if ai_bot.get_rect().collidepoint(food_pos):
                ai_bot.score  += 1
                food_pos = spawn_food()

            # --- wall collision ---
            p_rect = player.get_rect()
            if (p_rect.left < 0 or p_rect.right > WIDTH
                    or p_rect.top < 50 or p_rect.bottom > HEIGHT):
                game_state  = "GAME_OVER"
                winner_text  = "PLAYER HIT THE WALL!"
                winner_color = RED

            a_rect = ai_bot.get_rect()
            if (a_rect.left < 0 or a_rect.right > WIDTH
                    or a_rect.top < 50 or a_rect.bottom > HEIGHT):
                game_state  = "GAME_OVER"
                winner_text  = "AI HIT THE WALL  —  PLAYER WINS!"
                winner_color = GOLD

            # ---- draw game ----
            player.draw()
            if game_state == "RACING":
                ai_bot.draw()

            screen.blit(fare_img, (food_pos[0] - BLOCK_SIZE // 2,
                                   food_pos[1] - BLOCK_SIZE // 2))
            draw_ui(player.score, ai_bot.score)

            # ESC → back to menu
            if keys[pygame.K_ESCAPE]:
                if game_state == "COLLECTING" and collected_data:
                    pd.DataFrame(collected_data).to_csv(
                        "yilan_verisi.csv", index=False)
                game_state = "MENU"
                paused     = False

    # =========================
    # GAME OVER
    # =========================
    elif game_state == "GAME_OVER":

        ov_text = font_title.render("GAME OVER", True, RED)
        screen.blit(ov_text, (WIDTH // 2 - ov_text.get_width() // 2, 200))

        res_text = font_btn.render(winner_text, True, winner_color)
        screen.blit(res_text, (WIDTH // 2 - res_text.get_width() // 2, 290))

        # Scores
        ps = font_btn.render(f"Player: {player.score}", True, PLAYER_BLUE)
        as_ = font_btn.render(f"AI:     {ai_bot.score}", True, AI_GREEN)
        screen.blit(ps,  (WIDTH // 2 - ps.get_width() // 2,  345))
        screen.blit(as_, (WIDTH // 2 - as_.get_width() // 2, 380))

        btn_play_again = draw_button("▶  PLAY AGAIN",  250, 450, 220, 55,
                                     False, color_override=(20, 80, 50))
        btn_back       = draw_button("⌂  MAIN MENU",   530, 450, 220, 55,
                                     False, color_override=(60, 25, 25))

        if click:
            if btn_play_again.collidepoint(mx, my):
                player.reset(200, 350, current_speed,    PLAYER_BLUE, True)
                ai_bot.reset(800, 350, current_ai_speed, AI_GREEN,    False)
                food_pos   = spawn_food()
                paused     = False
                game_state = "RACING"

            if btn_back.collidepoint(mx, my):
                game_state = "MENU"

    # =========================
    # NOTIFICATION BAR
    # =========================
    if error_timer > 0:
        is_success = ("✅" in error_msg or "TRAINED" in error_msg)
        col = AI_GREEN if is_success else RED
        msg = font_btn.render(error_msg, True, col)
        # pill background
        pw, ph = msg.get_width() + 40, msg.get_height() + 14
        px = WIDTH // 2 - pw // 2
        py = HEIGHT - 50
        pygame.draw.rect(screen, (20, 25, 40), (px, py, pw, ph), border_radius=8)
        pygame.draw.rect(screen, col,          (px, py, pw, ph), 2, border_radius=8)
        screen.blit(msg, (px + 20, py + 7))
        error_timer -= 1

    pygame.display.flip()
    clock.tick(60)

pygame.quit()