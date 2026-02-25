import pygame
import random
import os

# --- 1. การตั้งค่าพื้นฐาน ---
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sorting Master: Ultimate Edition")

# สีและฟอนต์
WHITE, BLACK, RED, GREEN, BLUE, YELLOW = (255,255,255), (0,0,0), (200,50,50), (50,200,50), (50,50,200), (220,220,50)
GRAY, DARK_GRAY = (150,150,150), (50,50,50)
BIG_FONT = pygame.font.SysFont("Arial", 80, bold=True)
FONT = pygame.font.SysFont("Arial", 32, bold=True)
SMALL_FONT = pygame.font.SysFont("Arial", 22)

# --- 2. โหลดและจัดการรูปภาพ ---
def load_and_scale(name, size):
    try:
        img = pygame.image.load(name).convert_alpha()
        return pygame.transform.scale(img, size)
    except:
        surf = pygame.Surface(size)
        surf.fill(GRAY)
        return surf

# พื้นหลัง
menu_bg_img = load_and_scale("menu_bg.png", (WIDTH, HEIGHT))
game_bg_img = load_and_scale("factory_bg.png", (WIDTH, HEIGHT))
conveyor_img = load_and_scale("conveyor.png", (100, HEIGHT))

# ถังขยะ
bin_images = {
    "RECYCLE": load_and_scale("bin_recycle.png", (155, 130)),
    "WET": load_and_scale("bin_wet.png", (155, 130)),
    "GENERAL": load_and_scale("bin_general.png", (155, 130)),
    "HAZARDOUS": load_and_scale("bin_hazard.png", (155, 130))
}

# ขยะ
item_images = {
    "RECYCLE": load_and_scale("item_recycle.png", (65, 65)),
    "WET": load_and_scale("item_wet.png", (65, 65)),
    "GENERAL": load_and_scale("item_general.png", (65, 65)),
    "HAZARDOUS": load_and_scale("item_hazard.png", (65, 65))
}

# --- 3. ระบบจัดการคะแนน ---
SCORE_FILE = "highscores.txt"
def load_high_scores():
    if not os.path.exists(SCORE_FILE): return []
    scores = []
    try:
        with open(SCORE_FILE, "r") as f:
            for line in f:
                parts = line.strip().split(",")
                if len(parts) == 2: scores.append({"score": int(parts[0]), "time": int(parts[1])})
    except: pass
    scores.sort(key=lambda x: x["score"], reverse=True)
    return scores[:10]

def save_score(new_score, new_time):
    scores = load_high_scores()
    scores.append({"score": new_score, "time": new_time})
    scores.sort(key=lambda x: x["score"], reverse=True)
    with open(SCORE_FILE, "w") as f:
        for s in scores[:10]: f.write(f"{s['score']},{s['time']}\n")

# --- 4. คลาสและฟังก์ชัน UI ---
class Garbage:
    def __init__(self):
        self.type = random.choice(["WET", "RECYCLE", "GENERAL", "HAZARDOUS"])
        self.image = item_images[self.type]
        self.rect = self.image.get_rect(center=(WIDTH // 2, -50))
        self.dragging = False
        self.speed = random.uniform(2.5, 4.5)

    def move(self):
        if not self.dragging: self.rect.y += self.speed

    def draw(self):
        screen.blit(self.image, self.rect)

bins = [
    {"type": "RECYCLE", "rect": pygame.Rect(40, 465, 155, 130)},
    {"type": "WET", "rect": pygame.Rect(228, 465, 155, 130)},
    {"type": "GENERAL", "rect": pygame.Rect(416, 465, 155, 130)},
    {"type": "HAZARDOUS", "rect": pygame.Rect(605, 465, 155, 130)}
]

def draw_button(text, x, y, w, h, color, hover_color):
    mouse, click = pygame.mouse.get_pos(), pygame.mouse.get_pressed()
    rect = pygame.Rect(x, y, w, h)
    action = False
    if rect.collidepoint(mouse):
        pygame.draw.rect(screen, hover_color, rect, border_radius=12)
        if click[0] == 1: action = True
    else: pygame.draw.rect(screen, color, rect, border_radius=12)
    pygame.draw.rect(screen, BLACK, rect, 2, border_radius=12)
    txt_surf = SMALL_FONT.render(text, True, WHITE)
    screen.blit(txt_surf, txt_surf.get_rect(center=rect.center))
    return action

def draw_pause_button(x, y, w, h, color, hover_color):
    mouse, click = pygame.mouse.get_pos(), pygame.mouse.get_pressed()
    rect = pygame.Rect(x, y, w, h)
    action = False
    if rect.collidepoint(mouse):
        pygame.draw.rect(screen, hover_color, rect, border_radius=12)
        if click[0] == 1: action = True
    else: pygame.draw.rect(screen, color, rect, border_radius=12)
    pygame.draw.rect(screen, BLACK, rect, 2, border_radius=12)
    pygame.draw.rect(screen, WHITE, (rect.centerx - 7, rect.centery - 11, 5, 22))
    pygame.draw.rect(screen, WHITE, (rect.centerx + 2, rect.centery - 11, 5, 22))
    return action

# --- 5. ฟังก์ชันหลัก ---
def main():
    clock = pygame.time.Clock()
    state = 'START_MENU'
    score, lives, items, active_item = 0, 5, [], None
    start_ticks, total_paused_time, final_time, score_saved = 0, 0, 0, False
    
    SPAWN_EVENT = pygame.USEREVENT + 1
    pygame.time.set_timer(SPAWN_EVENT, 1500)

    running = True
    while running:
        if state == 'START_MENU':
            screen.blit(menu_bg_img, (0, 0))
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 120)); screen.blit(overlay, (0,0))
            
            title = BIG_FONT.render("SORTING MASTER", True, GREEN)
            screen.blit(title, (WIDTH//2 - title.get_width()//2, 40))
            
            # Leaderboard
            frame = pygame.Rect(WIDTH//2 - 200, 130, 400, 320)
            pygame.draw.rect(screen, (20, 20, 20, 200), frame, border_radius=20)
            pygame.draw.rect(screen, YELLOW, frame, 3, border_radius=20)
            
            high_scores = load_high_scores()
            for i, s in enumerate(high_scores):
                y_pos = 200 + (i * 22)
                screen.blit(SMALL_FONT.render(f"#{i+1} Score: {s['score']} ({s['time']}s)", True, WHITE), (WIDTH//2 - 100, y_pos))

            if draw_button("START", WIDTH//2 - 220, 480, 200, 50, BLUE, (100, 100, 255)):
                state, score, lives, items, score_saved = 'PLAYING', 0, 5, [], False
                start_ticks, total_paused_time = pygame.time.get_ticks(), 0; pygame.time.delay(200)
            if draw_button("QUIT", WIDTH//2 + 20, 480, 200, 50, RED, (255, 100, 100)): running = False

        else:
            screen.blit(game_bg_img, (0, 0))
            screen.blit(conveyor_img, (WIDTH // 2 - 50, 0))
            for b in bins: screen.blit(bin_images[b["type"]], b["rect"])

            if state == 'PLAYING':
                seconds = (pygame.time.get_ticks() - start_ticks - total_paused_time) // 1000
                if draw_pause_button(WIDTH - 85, 20, 60, 50, DARK_GRAY, GRAY):
                    state, pause_start = 'PAUSED', pygame.time.get_ticks(); pygame.time.delay(200)
                
                for event in pygame.event.get():
                    if event.type == pygame.QUIT: running = False
                    if event.type == SPAWN_EVENT: items.append(Garbage())
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        for item in reversed(items):
                            if item.rect.collidepoint(event.pos): item.dragging, active_item = True, item; break
                    if event.type == pygame.MOUSEBUTTONUP and active_item:
                        hit = False
                        for b in bins:
                            if b["rect"].colliderect(active_item.rect):
                                if b["type"] == active_item.type: score += 10
                                else: score = max(0, score-5); lives -= 1
                                items.remove(active_item); hit = True; break
                        if not hit: items.remove(active_item); lives -= 1
                        active_item = None
                    if event.type == pygame.MOUSEMOTION and active_item: active_item.rect.center = event.pos

                for item in items[:]:
                    item.move(); item.draw()
                    if item.rect.y > HEIGHT: items.remove(item); lives -= 1

                screen.blit(FONT.render(f"SCORE: {score}", True, WHITE), (20, 20))
                screen.blit(FONT.render(f"LIVES: {lives}", True, RED), (20, 60))
                if lives <= 0: state, final_time = 'GAME_OVER', seconds

            elif state == 'PAUSED':
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                overlay.fill((0,0,0,150)); screen.blit(overlay, (0,0))
                if draw_button("RESUME", WIDTH//2-80, 250, 160, 50, GREEN, (70,230,70)):
                    total_paused_time += pygame.time.get_ticks() - pause_start; state = 'PLAYING'
                if draw_button("MENU", WIDTH//2-80, 320, 160, 50, BLUE, (100,100,255)): state = 'START_MENU'

            elif state == 'GAME_OVER':
                if not score_saved: save_score(score, final_time); score_saved = True
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                overlay.fill((100,0,0,160)); screen.blit(overlay, (0,0))
                pygame.draw.rect(screen, WHITE, (WIDTH//2-150, 200, 300, 200), border_radius=20)
                screen.blit(FONT.render("GAME OVER", True, RED), (WIDTH//2-80, 220))
                screen.blit(SMALL_FONT.render(f"Score: {score} Time: {final_time}s", True, BLACK), (WIDTH//2-80, 280))
                if draw_button("MENU", WIDTH//2-60, 330, 120, 40, BLUE, (100,100,255)): state = 'START_MENU'

        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
        pygame.display.flip()
        clock.tick(60)
    pygame.quit()

if __name__ == "__main__": main()