import pygame
import random
import os

# --- 1. การตั้งค่าพื้นฐาน ---
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sorting Master: Professional Edition")

# สี (เพิ่มเติมสีสำหรับ Leaderboard)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 50, 50)
GOLD = (255, 215, 0)
SILVER = (192, 192, 192)
BRONZE = (205, 127, 50)
GRAY = (150, 150, 150)
DARK_GRAY = (30, 30, 30)

# ฟอนต์
BIG_FONT = pygame.font.SysFont("Arial", 70, bold=True)
FONT = pygame.font.SysFont("Arial", 32, bold=True)
SMALL_FONT = pygame.font.SysFont("Arial", 22, bold=True)

# --- 2. โหลดรูปภาพ ---
def load_img(name, size):
    try:
        img = pygame.image.load(name).convert_alpha()
        return pygame.transform.scale(img, size)
    except:
        surf = pygame.Surface(size)
        surf.fill(GRAY)
        return surf

# พื้นหลังและสายพาน
menu_bg = load_img("menu_bg.png", (WIDTH, HEIGHT))
game_bg = load_img("factory_bg.png", (WIDTH, HEIGHT))
conveyor_img = load_img("conveyor.png", (120, HEIGHT)) # ขนาดปรับตามความเหมาะสม

# ถังขยะและขยะ
bin_images = {
    "RECYCLE": load_img("bin_recycle.png", (155, 130)),
    "WET": load_img("bin_wet.png", (155, 130)),
    "GENERAL": load_img("bin_general.png", (155, 130)),
    "HAZARDOUS": load_img("bin_hazard.png", (155, 130))
}

item_images = {
    "RECYCLE": load_img("item_recycle.png", (65, 65)),
    "WET": load_img("item_wet.png", (65, 65)),
    "GENERAL": load_img("item_general.png", (65, 65)),
    "HAZARDOUS": load_img("item_hazard.png", (65, 65))
}

# --- 3. ระบบจัดการคะแนน ---
SCORE_FILE = "high_scores.txt"

def load_high_scores():
    if not os.path.exists(SCORE_FILE): return []
    scores = []
    with open(SCORE_FILE, "r") as f:
        for line in f:
            p = line.strip().split(",")
            if len(p) == 2: scores.append({"score": int(p[0]), "time": int(p[1])})
    scores.sort(key=lambda x: x["score"], reverse=True)
    return scores[:5]

def save_score(s, t):
    scores = load_high_scores()
    scores.append({"score": s, "time": t})
    scores.sort(key=lambda x: x["score"], reverse=True)
    with open(SCORE_FILE, "w") as f:
        for item in scores[:5]: f.write(f"{item['score']},{item['time']}\n")

# --- 4. ฟังก์ชันการวาด UI ปรับปรุงใหม่ ---
def draw_leaderboard(x, y, w, h):
    # วาดกรอบพื้นหลังกึ่งโปร่งใส
    overlay = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(overlay, (0, 0, 0, 200), (0, 0, w, h), border_radius=20)
    screen.blit(overlay, (x, y))
    pygame.draw.rect(screen, GOLD, (x, y, w, h), 3, border_radius=20)
    
    # หัวข้อ
    title = FONT.render("LEADERBOARD", True, (0, 255, 150))
    screen.blit(title, (x + w//2 - title.get_width()//2, y + 20))
    
    scores = load_high_scores()
    for i, s in enumerate(scores):
        color = GOLD if i == 0 else SILVER if i == 1 else BRONZE if i == 2 else WHITE
        y_pos = y + 80 + (i * 45)
        
        rank_txt = SMALL_FONT.render(f"#{i+1}", True, color)
        score_txt = SMALL_FONT.render(f"Score: {s['score']}", True, WHITE)
        time_txt = SMALL_FONT.render(f"{s['time']}s", True, GRAY)
        
        screen.blit(rank_txt, (x + 30, y_pos))
        screen.blit(score_txt, (x + 90, y_pos))
        screen.blit(time_txt, (x + 300, y_pos))

def draw_button(text, rect, color, hover_color):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    cur_color = hover_color if rect.collidepoint(mouse) else color
    
    pygame.draw.rect(screen, cur_color, rect, border_radius=10)
    pygame.draw.rect(screen, WHITE, rect, 2, border_radius=10)
    
    txt = SMALL_FONT.render(text, True, WHITE)
    screen.blit(txt, (rect.centerx - txt.get_width()//2, rect.centery - txt.get_height()//2))
    return rect.collidepoint(mouse) and click[0]

# --- 5. คลาสขยะ ---
class Garbage:
    def __init__(self):
        self.type = random.choice(["WET", "RECYCLE", "GENERAL", "HAZARDOUS"])
        self.image = item_images[self.type]
        self.rect = self.image.get_rect(center=(WIDTH//2, -50))
        self.speed = random.uniform(2.5, 4.0)
        self.dragging = False

    def move(self):
        if not self.dragging: self.rect.y += self.speed

# --- 6. ลูปเกมหลัก ---
def main():
    clock = pygame.time.Clock()
    state = 'MENU'
    score, lives = 0, 5
    items = []
    active_item = None
    start_ticks = 0
    score_saved = False

    bins = [
        {"type": "RECYCLE", "rect": pygame.Rect(40, 460, 155, 130)},
        {"type": "WET", "rect": pygame.Rect(228, 460, 155, 130)},
        {"type": "GENERAL", "rect": pygame.Rect(416, 460, 155, 130)},
        {"type": "HAZARDOUS", "rect": pygame.Rect(605, 460, 155, 130)}
    ]

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            
            if state == 'PLAYING':
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for item in reversed(items):
                        if item.rect.collidepoint(event.pos):
                            item.dragging = True
                            active_item = item
                            break
                if event.type == pygame.MOUSEBUTTONUP and active_item:
                    correct = False
                    for b in bins:
                        if b["rect"].colliderect(active_item.rect):
                            if b["type"] == active_item.type:
                                score += 10
                                correct = True
                            else:
                                lives -= 1
                            items.remove(active_item)
                            break
                    if not correct and active_item in items:
                        # ถ้าลากไปวางผิดที่/นอกถัง
                        items.remove(active_item)
                        lives -= 1
                    active_item = None
                if event.type == pygame.MOUSEMOTION and active_item:
                    active_item.rect.center = event.pos

        # --- การจัดการสถานะ (State Machine) ---
        if state == 'MENU':
            screen.blit(menu_bg, (0, 0))
            draw_leaderboard(WIDTH//2 - 200, 100, 400, 350)
            if draw_button("START GAME", pygame.Rect(WIDTH//2 - 100, 480, 200, 50), (50, 150, 50), (70, 200, 70)):
                state, score, lives, items, score_saved = 'PLAYING', 0, 5, [], False
                start_ticks = pygame.time.get_ticks()
                pygame.time.delay(200)

        elif state == 'PLAYING':
            screen.blit(game_bg, (0, 0))
            screen.blit(conveyor_img, (WIDTH//2 - 60, 0))
            
            for b in bins: screen.blit(bin_images[b["type"]], b["rect"])
            
            # สุ่มเกิดขยะ
            if random.random() < 0.02: items.append(Garbage())
            
            for item in items[:]:
                item.move()
                screen.blit(item.image, item.rect)
                if item.rect.y > HEIGHT:
                    items.remove(item)
                    lives -= 1
            
            # UI แสดงผล
            screen.blit(FONT.render(f"Score: {score}", True, WHITE), (20, 20))
            screen.blit(FONT.render(f"Lives: {lives}", True, RED), (20, 60))
            
            if lives <= 0: state = 'GAMEOVER'

        elif state == 'GAMEOVER':
            play_time = (pygame.time.get_ticks() - start_ticks) // 1000
            if not score_saved:
                save_score(score, play_time)
                score_saved = True
            
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            
            txt = BIG_FONT.render("GAME OVER", True, RED)
            screen.blit(txt, (WIDTH//2 - txt.get_width()//2, 150))
            
            res_txt = FONT.render(f"Final Score: {score}", True, WHITE)
            screen.blit(res_txt, (WIDTH//2 - res_txt.get_width()//2, 250))
            
            if draw_button("BACK TO MENU", pygame.Rect(WIDTH//2 - 120, 350, 240, 50), (50, 50, 150), (80, 80, 250)):
                state = 'MENU'
                pygame.time.delay(200)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()