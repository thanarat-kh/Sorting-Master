import pygame
import random
import os

# --- 1. การตั้งค่าพื้นฐาน ---
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sorting Master: Ultimate Edition")

# สีสันต่างๆ
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 50, 50)
GREEN = (50, 205, 50)
BLUE = (100, 150, 255)
GOLD = (255, 215, 0)
GRAY = (150, 150, 150)
DARK_GRAY = (30, 30, 30)

# ฟอนต์
try:
    BIG_FONT = pygame.font.SysFont("Arial", 65, bold=True)
    FONT = pygame.font.SysFont("Arial", 32, bold=True)
    SMALL_FONT = pygame.font.SysFont("Arial", 22, bold=True)
except:
    BIG_FONT = pygame.font.Font(None, 80)
    FONT = pygame.font.Font(None, 40)
    SMALL_FONT = pygame.font.Font(None, 30)

# --- 2. โหลดรูปภาพ ---
def load_img(name, size):
    try:
        img = pygame.image.load(name).convert_alpha()
        return pygame.transform.scale(img, size)
    except:
        surf = pygame.Surface(size, pygame.SRCALPHA)
        surf.fill((150, 150, 150, 200))
        return surf

menu_bg = load_img("menu_bg.png", (WIDTH, HEIGHT))
game_bg = load_img("factory_bg.png", (WIDTH, HEIGHT))
conveyor_img = load_img("conveyor.png", (120, HEIGHT))

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

# --- 3. ระบบจัดการคะแนน (Top 10) ---
SCORE_FILE = "high_scores.txt"

def load_high_scores():
    if not os.path.exists(SCORE_FILE): return []
    scores = []
    with open(SCORE_FILE, "r") as f:
        for line in f:
            p = line.strip().split(",")
            if len(p) == 2: scores.append({"score": int(p[0]), "time": int(p[1])})
    scores.sort(key=lambda x: x["score"], reverse=True)
    return scores[:10]

def save_score(s, t):
    scores = load_high_scores()
    scores.append({"score": s, "time": t})
    scores.sort(key=lambda x: x["score"], reverse=True)
    with open(SCORE_FILE, "w") as f:
        for item in scores[:10]: f.write(f"{item['score']},{item['time']}\n")

# --- 4. ฟังก์ชันการวาด UI ---
def draw_button(text, rect, color, hover_color):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    is_hover = rect.collidepoint(mouse)
    cur_color = hover_color if is_hover else color
    
    pygame.draw.rect(screen, cur_color, rect, border_radius=10)
    pygame.draw.rect(screen, BLACK, rect, 2, border_radius=10)
    
    txt = SMALL_FONT.render(text, True, WHITE)
    screen.blit(txt, (rect.centerx - txt.get_width()//2, rect.centery - txt.get_height()//2))
    
    return is_hover and click[0]

def draw_custom_menu(scores):
    screen.blit(menu_bg, (0, 0))
    
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 120))
    screen.blit(overlay, (0, 0))

    title_text = "SORTING MASTER"
    title_surf = BIG_FONT.render(title_text, True, GREEN)
    title_rect = title_surf.get_rect(center=(WIDTH // 2, 80))
    shadow_surf = BIG_FONT.render(title_text, True, BLACK)
    screen.blit(shadow_surf, (title_rect.x + 4, title_rect.y + 4))
    screen.blit(title_surf, title_rect)

    if len(scores) > 0:
        box_rect = pygame.Rect(WIDTH // 2 - 250, 140, 500, 340)
        pygame.draw.rect(screen, (20, 20, 20), box_rect, border_radius=15)
        pygame.draw.rect(screen, GOLD, box_rect, 3, border_radius=15)

        header_surf = FONT.render("TOP 10 SCORES", True, GOLD)
        screen.blit(header_surf, (box_rect.centerx - header_surf.get_width() // 2, box_rect.y + 15))
        pygame.draw.line(screen, WHITE, (box_rect.x + 40, box_rect.y + 55), (box_rect.right - 40, box_rect.y + 55), 2)

        for i in range(len(scores)):
            y_pos = box_rect.y + 70 + (i * 25)
            rank_str = f"#{i+1}"
            s_val = scores[i]['score']
            t_val = scores[i]['time']

            screen.blit(SMALL_FONT.render(rank_str, True, WHITE), (box_rect.x + 80, y_pos))
            screen.blit(SMALL_FONT.render(f"{s_val}", True, GREEN), (box_rect.x + 220, y_pos))
            screen.blit(SMALL_FONT.render(f"{t_val}s", True, BLUE), (box_rect.x + 360, y_pos))
    else:
        prompt_txt = FONT.render("BE THE FIRST TO PLAY!", True, WHITE)
        screen.blit(prompt_txt, (WIDTH // 2 - prompt_txt.get_width() // 2, 280))

    btn_start_rect = pygame.Rect(WIDTH // 2 - 230, 500, 210, 55)
    btn_quit_rect = pygame.Rect(WIDTH // 2 + 20, 500, 210, 55)

    start_clicked = draw_button("START GAME", btn_start_rect, (40, 50, 180), (60, 80, 255))
    quit_clicked = draw_button("QUIT GAME", btn_quit_rect, (180, 40, 40), (255, 60, 60))
    
    return start_clicked, quit_clicked

# --- 5. คลาสขยะ ---
class Garbage:
    def __init__(self):
        self.type = random.choice(["WET", "RECYCLE", "GENERAL", "HAZARDOUS"])
        self.image = item_images[self.type]
        self.rect = self.image.get_rect(center=(WIDTH//2, -50))
        self.speed = random.uniform(2.5, 4.0)
        self.dragging = False

    def move(self):
        if not self.dragging: 
            self.rect.y += self.speed

# --- 6. ลูปเกมหลัก ---
def main():
    clock = pygame.time.Clock()
    state = 'MENU'
    score, lives = 0, 5
    items = []
    active_item = None
    start_ticks = 0
    final_time = 0
    score_saved = False
    
    # ตัวแปรจัดการระบบ Pause
    total_paused_time = 0
    pause_start_ticks = 0

    bins = [
        {"type": "RECYCLE", "rect": pygame.Rect(40, 460, 155, 130)},
        {"type": "WET", "rect": pygame.Rect(228, 460, 155, 130)},
        {"type": "GENERAL", "rect": pygame.Rect(416, 460, 155, 130)},
        {"type": "HAZARDOUS", "rect": pygame.Rect(605, 460, 155, 130)}
    ]

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # ระบบ Drag & Drop เมื่อกำลังเล่น (ไม่รับคำสั่งเมาส์ถ้าหยุดเกมอยู่)
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
                                lives -= 1 # หักแค่ชีวิต ไม่หักคะแนน
                            items.remove(active_item)
                            break
                    if not correct and active_item in items:
                        items.remove(active_item)
                        lives -= 1
                    active_item = None
                
                if event.type == pygame.MOUSEMOTION and active_item:
                    active_item.rect.center = event.pos

        # ==========================================
        # การจัดการหน้าจอตามสถานะ (State Machine)
        # ==========================================

        if state == 'MENU':
            scores = load_high_scores()
            start_clicked, quit_clicked = draw_custom_menu(scores)
            
            if start_clicked:
                state = 'PLAYING'
                score = 0
                lives = 5
                items = []
                score_saved = False
                
                # รีเซ็ตเวลาเริ่มต้นและเวลาที่หยุดพักใหม่ทั้งหมด
                start_ticks = pygame.time.get_ticks()
                total_paused_time = 0 
                pygame.time.delay(200)
            if quit_clicked:
                running = False

        elif state == 'PLAYING':
            screen.blit(game_bg, (0, 0))
            screen.blit(conveyor_img, (WIDTH//2 - 60, 0))
            
            for b in bins: 
                screen.blit(bin_images[b["type"]], b["rect"])
            
            if random.random() < 0.02: 
                items.append(Garbage())
            
            for item in items[:]:
                item.move()
                screen.blit(item.image, item.rect)
                if item.rect.y > HEIGHT:
                    items.remove(item)
                    lives -= 1
            
            # วาด UI คะแนนและชีวิต
            screen.blit(FONT.render(f"SCORE: {score}", True, WHITE), (20, 20))
            screen.blit(FONT.render(f"LIVES: {lives}", True, RED), (20, 60))
            
            # === ปุ่ม PAUSE ===
            pause_btn_rect = pygame.Rect(WIDTH - 120, 20, 100, 45)
            if draw_button("PAUSE", pause_btn_rect, (100, 100, 100), (150, 150, 150)):
                state = 'PAUSED'
                pause_start_ticks = pygame.time.get_ticks() # เก็บเวลาที่เริ่มกดหยุด
                pygame.time.delay(200)

            if lives <= 0: 
                state = 'GAMEOVER'
                # ลบเวลาที่หยุดเกมออกจากการคำนวณเวลาเล่นทั้งหมด
                final_time = (pygame.time.get_ticks() - start_ticks - total_paused_time) // 1000

        elif state == 'PAUSED':
            # วาดพื้นหลังเดิมค้างไว้แต่ทำให้ขยะหยุดนิ่ง
            screen.blit(game_bg, (0, 0))
            screen.blit(conveyor_img, (WIDTH//2 - 60, 0))
            for b in bins: screen.blit(bin_images[b["type"]], b["rect"])
            for item in items: screen.blit(item.image, item.rect)

            # วาดฟิล์มสีดำโปร่งใสทับ
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))

            # ข้อความ PAUSED
            txt = BIG_FONT.render("PAUSED", True, GOLD)
            screen.blit(txt, (WIDTH//2 - txt.get_width()//2, 180))

            # ปุ่ม Resume และ Menu
            if draw_button("RESUME", pygame.Rect(WIDTH//2 - 100, 300, 200, 50), GREEN, (80, 255, 80)):
                state = 'PLAYING'
                # นำเวลาที่หยุดไปสะสมใน total_paused_time 
                total_paused_time += pygame.time.get_ticks() - pause_start_ticks
                pygame.time.delay(200)

            if draw_button("MAIN MENU", pygame.Rect(WIDTH//2 - 100, 370, 200, 50), RED, (255, 80, 80)):
                state = 'MENU'
                pygame.time.delay(200)

        elif state == 'GAMEOVER':
            if not score_saved:
                save_score(score, final_time)
                score_saved = True
            
            screen.blit(game_bg, (0, 0))
            screen.blit(conveyor_img, (WIDTH//2 - 60, 0))
            for b in bins: 
                screen.blit(bin_images[b["type"]], b["rect"])

            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            
            txt = BIG_FONT.render("GAME OVER", True, RED)
            screen.blit(txt, (WIDTH//2 - txt.get_width()//2, 150))
            
            res_txt = FONT.render(f"Final Score: {score}  |  Time: {final_time}s", True, WHITE)
            screen.blit(res_txt, (WIDTH//2 - res_txt.get_width()//2, 250))
            
            if draw_button("BACK TO MENU", pygame.Rect(WIDTH//2 - 120, 350, 240, 50), BLUE, (80, 80, 255)):
                state = 'MENU'
                pygame.time.delay(200)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()