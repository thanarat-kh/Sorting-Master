import pygame
import random
import os

# --- 1. การตั้งค่าพื้นฐาน ---
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sorting Master - Score & Time Leaderboard")

# สี
WHITE, BLACK, RED, GREEN, BLUE, YELLOW = (255,255,255), (0,0,0), (200,50,50), (50,200,50), (50,50,200), (220,220,50)
HAZARD_RED, GRAY, DARK_GRAY = (180, 0, 0), (150,150,150), (50,50,50)

# ฟอนต์
BIG_FONT = pygame.font.SysFont("Arial", 80, bold=True)
FONT = pygame.font.SysFont("Arial", 32, bold=True)
SMALL_FONT = pygame.font.SysFont("Arial", 22)

# --- ระบบจัดการคะแนน (High Score with Time) ---
SCORE_FILE = "highscores.txt"

def load_high_scores():
    if not os.path.exists(SCORE_FILE): return []
    scores = []
    with open(SCORE_FILE, "r") as f:
        for line in f:
            parts = line.strip().split(",")
            if len(parts) == 2:
                scores.append({"score": int(parts[0]), "time": int(parts[1])})
    # เรียงตามคะแนน (Score) เป็นหลัก
    scores.sort(key=lambda x: x["score"], reverse=True)
    return scores[:10]

def save_score(new_score, new_time):
    scores = load_high_scores()
    scores.append({"score": new_score, "time": new_time})
    scores.sort(key=lambda x: x["score"], reverse=True)
    with open(SCORE_FILE, "w") as f:
        for s in scores[:10]:
            f.write(f"{s['score']},{s['time']}\n")

# --- โหลดรูปภาพพื้นหลัง ---
try:
    bg_image = pygame.image.load("factory_bg.png")
    bg_image = pygame.transform.scale(bg_image, (WIDTH, HEIGHT))
except:
    bg_image = None

# --- คลาสขยะ (แนวตั้ง) ---
class Garbage:
    def __init__(self):
        self.type = random.choice(["WET", "RECYCLE", "GENERAL", "HAZARDOUS"])
        self.rect = pygame.Rect(WIDTH // 2 - 30, -60, 60, 60)
        self.dragging = False
        self.speed = random.uniform(3.0, 5.0) 
        if self.type == "WET": self.color = GREEN
        elif self.type == "RECYCLE": self.color = YELLOW
        elif self.type == "GENERAL": self.color = BLUE
        else: self.color = HAZARD_RED

    def move(self):
        if not self.dragging: self.rect.y += self.speed

    def draw(self):
        pygame.draw.rect(screen, self.color, self.rect, border_radius=10)
        pygame.draw.rect(screen, BLACK, self.rect, 2, border_radius=10)
        label = SMALL_FONT.render(self.type[0], True, WHITE)
        screen.blit(label, (self.rect.x + 22, self.rect.y + 18))

# --- ข้อมูลถังขยะ ---
bins = [
    {"type": "RECYCLE", "rect": pygame.Rect(40, 470, 160, 110), "color": YELLOW, "label": "RECYCLE"},
    {"type": "WET", "rect": pygame.Rect(230, 470, 160, 110), "color": GREEN, "label": "WET"},
    {"type": "GENERAL", "rect": pygame.Rect(420, 470, 160, 110), "color": BLUE, "label": "GENERAL"},
    {"type": "HAZARDOUS", "rect": pygame.Rect(610, 470, 160, 110), "color": HAZARD_RED, "label": "HAZARD"}
]

def draw_button(text, x, y, w, h, color, hover_color):
    mouse, click = pygame.mouse.get_pos(), pygame.mouse.get_pressed()
    rect = pygame.Rect(x, y, w, h)
    action = False
    if rect.collidepoint(mouse):
        pygame.draw.rect(screen, hover_color, rect, border_radius=12)
        if click[0] == 1: action = True
    else:
        pygame.draw.rect(screen, color, rect, border_radius=12)
    pygame.draw.rect(screen, BLACK, rect, 2, border_radius=12)
    txt_surf = SMALL_FONT.render(text, True, WHITE)
    screen.blit(txt_surf, txt_surf.get_rect(center=rect.center))
    return action

# --- ฟังก์ชันหลัก ---
def main():
    clock = pygame.time.Clock()
    state = 'START_MENU'
    score, lives, items, active_item = 0, 5, [], None
    start_ticks, total_paused_time, final_time, score_saved = 0, 0, 0, False
    
    SPAWN_EVENT = pygame.USEREVENT + 1
    pygame.time.set_timer(SPAWN_EVENT, 1300)

    running = True
    while running:
        if bg_image: screen.blit(bg_image, (0, 0))
        else: screen.fill((200, 200, 200))

        if state == 'START_MENU':
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            screen.blit(overlay, (0,0))
            title = BIG_FONT.render("SORTING MASTER", True, GREEN)
            screen.blit(title, (WIDTH//2 - title.get_width()//2, 50))
            
            # --- Leaderboard Header ---
            hs_label = FONT.render("LEADERBOARD (TOP 10)", True, YELLOW)
            screen.blit(hs_label, (WIDTH//2 - hs_label.get_width()//2, 140))
            header = SMALL_FONT.render("RANK     SCORE      TIME", True, GRAY)
            screen.blit(header, (WIDTH//2 - 130, 185))

            high_scores = load_high_scores()
            for i, s in enumerate(high_scores):
                rank_txt = SMALL_FONT.render(f"#{i+1}", True, WHITE)
                score_txt = SMALL_FONT.render(f"{s['score']}", True, GREEN)
                time_txt = SMALL_FONT.render(f"{s['time']}s", True, BLUE)
                
                y_pos = 220 + (i * 25)
                screen.blit(rank_txt, (WIDTH//2 - 130, y_pos))
                screen.blit(score_txt, (WIDTH//2 - 30, y_pos))
                screen.blit(time_txt, (WIDTH//2 + 70, y_pos))

            if draw_button("START GAME", WIDTH//2 - 250, 510, 220, 50, BLUE, (100, 100, 255)):
                state, score, lives, items, score_saved = 'PLAYING', 0, 5, [], False
                start_ticks, total_paused_time = pygame.time.get_ticks(), 0
                pygame.time.delay(200)
            if draw_button("QUIT GAME", WIDTH//2 + 30, 510, 220, 50, RED, (255, 100, 100)):
                running = False

        elif state == 'PLAYING':
            seconds_passed = (pygame.time.get_ticks() - start_ticks - total_paused_time) // 1000
            pygame.draw.rect(screen, (80, 80, 80), (WIDTH // 2 - 40, 0, 80, HEIGHT))
            for b in bins:
                pygame.draw.rect(screen, b["color"], b["rect"], border_top_left_radius=15, border_top_right_radius=15)
                pygame.draw.rect(screen, BLACK, b["rect"], 3, border_top_left_radius=15, border_top_right_radius=15)
                screen.blit(SMALL_FONT.render(b["label"], True, BLACK), (b["rect"].centerx - 35, b["rect"].y + 40))

            if draw_button("PAUSE ||", WIDTH - 130, 20, 110, 45, DARK_GRAY, GRAY):
                state, pause_start_tick = 'PAUSED', pygame.time.get_ticks()
                pygame.time.delay(200)
            
            t_label = FONT.render(f"{seconds_passed}s", True, YELLOW)
            screen.blit(t_label, (WIDTH - 130 + (55 - t_label.get_width()//2), 75))

            for event in pygame.event.get():
                if event.type == pygame.QUIT: running = False
                if event.type == SPAWN_EVENT: items.append(Garbage())
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for item in reversed(items):
                        if item.rect.collidepoint(event.pos):
                            item.dragging, active_item = True, item
                            break
                if event.type == pygame.MOUSEBUTTONUP:
                    if active_item:
                        hit_bin = False
                        for b in bins:
                            if b["rect"].colliderect(active_item.rect):
                                if b["type"] == active_item.type: score += 10
                                else: score = max(0, score - 5); lives -= 1
                                items.remove(active_item); hit_bin = True; break
                        if not hit_bin:
                            if active_item in items: items.remove(active_item)
                            lives -= 1
                        active_item = None
                if event.type == pygame.MOUSEMOTION and active_item and active_item.dragging:
                    active_item.rect.center = event.pos

            for item in items[:]:
                item.move(); item.draw()
                if item.rect.y > HEIGHT: items.remove(item); lives -= 1

            screen.blit(FONT.render(f"SCORE: {score}", True, WHITE), (20, 20))
            screen.blit(FONT.render(f"LIVES: {lives}", True, RED), (20, 60))
            if lives <= 0: state, final_time = 'GAME_OVER', seconds_passed

        elif state == 'PAUSED':
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0,0))
            if draw_button("RESUME", WIDTH//2-100, 250, 200, 50, GREEN, (70, 230, 70)):
                total_paused_time += pygame.time.get_ticks() - pause_start_tick
                state = 'PLAYING'; pygame.time.delay(200)
            if draw_button("MENU", WIDTH//2-100, 320, 200, 50, BLUE, (100, 100, 255)):
                state = 'START_MENU'; pygame.time.delay(200)

        elif state == 'GAME_OVER':
            if not score_saved:
                save_score(score, final_time)
                score_saved = True
            
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((100, 0, 0, 180)); screen.blit(overlay, (0,0))
            pygame.draw.rect(screen, WHITE, (WIDTH//2-200, 150, 400, 320), border_radius=20)
            
            title = FONT.render("GAME OVER", True, RED)
            screen.blit(title, (WIDTH//2 - title.get_width()//2, 180))
            s_res = FONT.render(f"Final Score: {score}", True, BLACK)
            t_res = FONT.render(f"Time: {final_time}s", True, DARK_GRAY)
            screen.blit(s_res, (WIDTH//2 - s_res.get_width()//2, 250))
            screen.blit(t_res, (WIDTH//2 - t_res.get_width()//2, 300))
            
            if draw_button("RESTART", WIDTH//2-160, 380, 140, 50, GREEN, (70, 230, 70)):
                state, score, lives, items, score_saved = 'PLAYING', 0, 5, [], False
                start_ticks, total_paused_time = pygame.time.get_ticks(), 0; pygame.time.delay(200)
            if draw_button("MENU", WIDTH//2+20, 380, 140, 50, BLUE, (100, 100, 255)):
                state = 'START_MENU'; pygame.time.delay(200)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False

        pygame.display.flip()
        clock.tick(60)
    pygame.quit()

if __name__ == "__main__":
    main()