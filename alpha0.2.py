import pygame
import random

# --- 1. การตั้งค่าพื้นฐาน ---
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sorting Master - เมนูเริ่มเกม")

# สี
WHITE  = (255, 255, 255)
BLACK  = (0, 0, 0)
GRAY   = (150, 150, 150)
DARK_GRAY = (100, 100, 100)
RED    = (200, 50, 50)
GREEN  = (50, 200, 50)
BLUE   = (50, 50, 200)
YELLOW = (220, 220, 50)
LIGHT_BG = (240, 240, 240)

# ฟอนต์
BIG_FONT = pygame.font.SysFont("Arial", 80, bold=True)
FONT = pygame.font.SysFont("Arial", 32, bold=True)
SMALL_FONT = pygame.font.SysFont("Arial", 24)

TYPES = ["WET", "RECYCLE", "GENERAL"]

# --- 2. คลาสขยะ ---
class Garbage:
    def __init__(self):
        self.type = random.choice(TYPES)
        self.rect = pygame.Rect(-60, HEIGHT // 2 - 30, 60, 60)
        self.dragging = False
        self.speed = random.uniform(2.0, 4.0) 
        
        if self.type == "WET": self.color = GREEN
        elif self.type == "RECYCLE": self.color = BLUE
        else: self.color = YELLOW

    def move(self):
        if not self.dragging:
            self.rect.x += self.speed

    def draw(self):
        pygame.draw.rect(screen, self.color, self.rect, border_radius=8)
        pygame.draw.rect(screen, BLACK, self.rect, 2, border_radius=8)
        label = SMALL_FONT.render(self.type[0], True, WHITE)
        screen.blit(label, (self.rect.x + 20, self.rect.y + 15))

# --- 3. ข้อมูลถังขยะ ---
bins = [
    {"type": "WET", "rect": pygame.Rect(100, 450, 150, 110), "color": GREEN, "label": "WET"},
    {"type": "RECYCLE", "rect": pygame.Rect(325, 450, 150, 110), "color": BLUE, "label": "RECYCLE"},
    {"type": "GENERAL", "rect": pygame.Rect(550, 450, 150, 110), "color": YELLOW, "label": "GENERAL"},
]

# --- 4. ฟังก์ชันวาดปุ่ม (Button Helper) ---
def draw_button(text, x, y, w, h, color, hover_color):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    rect = pygame.Rect(x, y, w, h)
    
    action = False
    if rect.collidepoint(mouse):
        pygame.draw.rect(screen, hover_color, rect, border_radius=10)
        if click[0] == 1:
            action = True
    else:
        pygame.draw.rect(screen, color, rect, border_radius=10)
    
    pygame.draw.rect(screen, BLACK, rect, 2, border_radius=10)
    txt_surf = SMALL_FONT.render(text, True, WHITE)
    txt_rect = txt_surf.get_rect(center=rect.center)
    screen.blit(txt_surf, txt_rect)
    return action

# --- 5. ฟังก์ชันหลัก ---
def main():
    clock = pygame.time.Clock()
    
    # สถานะของเกม: 'START_MENU', 'PLAYING', 'GAME_OVER'
    state = 'START_MENU'
    
    # ตัวแปรในเกม
    score = 0
    lives = 5
    items = []
    active_item = None
    start_ticks = 0
    
    SPAWN_EVENT = pygame.USEREVENT + 1
    pygame.time.set_timer(SPAWN_EVENT, 1200)

    running = True
    while running:
        # --- หน้าเมนูเริ่มเกม ---
        if state == 'START_MENU':
            screen.fill(LIGHT_BG)
            title = BIG_FONT.render("SORTING MASTER", True, GREEN)
            screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 150))
            
            instr = SMALL_FONT.render("Drag garbage to the correct bins!", True, BLACK)
            screen.blit(instr, (WIDTH//2 - instr.get_width()//2, HEIGHT//2 - 50))

            if draw_button("START GAME", WIDTH//2 - 100, HEIGHT//2 + 50, 200, 60, BLUE, (100, 100, 255)):
                state = 'PLAYING'
                start_ticks = pygame.time.get_ticks() # เริ่มนับเวลาเมื่อกดเริ่ม
                score = 0
                lives = 5
                items = []
                pygame.time.delay(200) # ป้องกันการคลิกซ้ำซ้อน

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

        # --- หน้าตอนเล่นเกม ---
        elif state == 'PLAYING':
            screen.fill(LIGHT_BG)
            seconds_passed = (pygame.time.get_ticks() - start_ticks) // 1000

            pygame.draw.rect(screen, GRAY, (0, HEIGHT // 2 - 10, WIDTH, 20))
            for b in bins:
                pygame.draw.rect(screen, b["color"], b["rect"], border_top_left_radius=10, border_top_right_radius=10)
                pygame.draw.rect(screen, BLACK, b["rect"], 3, border_top_left_radius=10, border_top_right_radius=10)
                label = FONT.render(b["label"], True, BLACK)
                screen.blit(label, (b["rect"].centerx - label.get_width()//2, b["rect"].y + 35))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == SPAWN_EVENT:
                    items.append(Garbage())
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for item in reversed(items):
                        if item.rect.collidepoint(event.pos):
                            item.dragging = True
                            active_item = item
                            break
                if event.type == pygame.MOUSEBUTTONUP:
                    if active_item:
                        hit_bin = False
                        for b in bins:
                            if b["rect"].colliderect(active_item.rect):
                                if b["type"] == active_item.type: score += 10
                                else: score = max(0, score - 5); lives -= 1
                                items.remove(active_item)
                                hit_bin = True
                                break
                        if not hit_bin:
                            if active_item in items: items.remove(active_item)
                            lives -= 1
                        active_item = None
                if event.type == pygame.MOUSEMOTION:
                    if active_item and active_item.dragging:
                        active_item.rect.center = event.pos

            for item in items[:]:
                item.move()
                item.draw()
                if item.rect.x > WIDTH:
                    items.remove(item)
                    lives -= 1

            screen.blit(FONT.render(f"SCORE: {score}", True, BLACK), (20, 20))
            screen.blit(FONT.render(f"LIVES: {lives}", True, RED), (WIDTH - 160, 20))
            time_txt = FONT.render(f"TIME: {seconds_passed}s", True, BLUE)
            screen.blit(time_txt, time_txt.get_rect(center=(WIDTH // 2, 35)))

            if lives <= 0:
                state = 'GAME_OVER'
                final_time = seconds_passed # ล็อกเวลาที่ทำได้

        # --- หน้าจอจบเกม ---
        elif state == 'GAME_OVER':
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0,0))

            title = BIG_FONT.render("GAME OVER", True, RED)
            screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 180))

            score_res = FONT.render(f"Final Score: {score}", True, WHITE)
            time_res = FONT.render(f"Survival Time: {final_time}s", True, WHITE)
            screen.blit(score_res, (WIDTH//2 - score_res.get_width()//2, HEIGHT//2 - 80))
            screen.blit(time_res, (WIDTH//2 - time_res.get_width()//2, HEIGHT//2 - 30))

            if draw_button("RESTART", WIDTH//2 - 160, HEIGHT//2 + 60, 140, 50, GREEN, (70, 230, 70)):
                # รีเซ็ตตัวแปรเพื่อเริ่มใหม่
                score = 0
                lives = 5
                items = []
                start_ticks = pygame.time.get_ticks()
                state = 'PLAYING'
                pygame.time.delay(200)
            
            if draw_button("QUIT", WIDTH//2 + 20, HEIGHT//2 + 60, 140, 50, DARK_GRAY, GRAY):
                running = False

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()