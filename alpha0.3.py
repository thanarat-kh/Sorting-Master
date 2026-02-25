import pygame
import random

# --- 1. การตั้งค่าพื้นฐาน ---
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sorting Master - Hazardous Waste Update")

# สี
WHITE, BLACK, RED, GREEN, BLUE, YELLOW = (255,255,255), (0,0,0), (200,50,50), (50,200,50), (50,50,200), (220,220,50)
HAZARD_RED = (180, 0, 0) # สีแดงสำหรับขยะอันตราย
GRAY, DARK_GRAY = (150,150,150), (50,50,50)

# ฟอนต์
BIG_FONT = pygame.font.SysFont("Arial", 80, bold=True)
FONT = pygame.font.SysFont("Arial", 32, bold=True)
SMALL_FONT = pygame.font.SysFont("Arial", 22) # ปรับเล็กลงนิดหน่อยเพื่อให้พอดีถัง

# --- โหลดรูปภาพพื้นหลัง ---
try:
    bg_image = pygame.image.load("factory_bg.png")
    bg_image = pygame.transform.scale(bg_image, (WIDTH, HEIGHT))
except:
    bg_image = None

# --- 2. คลาสขยะ ---
class Garbage:
    def __init__(self):
        # เพิ่มประเภท HAZARDOUS
        self.type = random.choice(["WET", "RECYCLE", "GENERAL", "HAZARDOUS"])
        self.rect = pygame.Rect(-60, 275, 60, 60)
        self.dragging = False
        self.speed = random.uniform(2.5, 4.5) 
        
        if self.type == "WET": self.color = GREEN
        elif self.type == "RECYCLE": self.color = BLUE
        elif self.type == "GENERAL": self.color = YELLOW
        else: self.color = HAZARD_RED # สีแดงสำหรับอันตราย

    def move(self):
        if not self.dragging:
            self.rect.x += self.speed

    def draw(self):
        pygame.draw.rect(screen, self.color, self.rect, border_radius=10)
        pygame.draw.rect(screen, BLACK, self.rect, 2, border_radius=10)
        # แสดงตัวอักษรย่อ (W, R, G, H)
        label = SMALL_FONT.render(self.type[0], True, WHITE)
        screen.blit(label, (self.rect.x + 22, self.rect.y + 18))

# --- 3. ข้อมูลถังขยะ (ปรับตำแหน่งใหม่ให้รองรับ 4 ถัง) ---
# เรียงเป็น: รีไซเคิล(น้ำเงิน), ขยะเปียก(เขียว), ขยะทั่วไป(เหลือง), ขยะอันตราย(แดง)
bins = [
    {"type": "RECYCLE", "rect": pygame.Rect(40, 440, 160, 120), "color": BLUE, "label": "RECYCLE"},
    {"type": "WET", "rect": pygame.Rect(230, 440, 160, 120), "color": GREEN, "label": "WET"},
    {"type": "GENERAL", "rect": pygame.Rect(420, 440, 160, 120), "color": YELLOW, "label": "GENERAL"},
    {"type": "HAZARDOUS", "rect": pygame.Rect(610, 440, 160, 120), "color": HAZARD_RED, "label": "HAZARD"}
]

# --- 4. ฟังก์ชันวาดปุ่ม ---
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

# --- 5. ฟังก์ชันหลัก ---
def main():
    clock = pygame.time.Clock()
    state = 'START_MENU'
    score, lives, items, active_item = 0, 5, [], None
    start_ticks, total_paused_time, final_time = 0, 0, 0
    
    SPAWN_EVENT = pygame.USEREVENT + 1
    pygame.time.set_timer(SPAWN_EVENT, 1500)

    running = True
    while running:
        if bg_image:
            screen.blit(bg_image, (0, 0))
        else:
            screen.fill((200, 200, 200))

        if state == 'START_MENU':
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0,0))
            title = BIG_FONT.render("SORTING MASTER", True, GREEN)
            screen.blit(title, (WIDTH//2 - title.get_width()//2, 150))
            if draw_button("START GAME", WIDTH//2 - 110, 300, 220, 60, BLUE, (100, 100, 255)):
                state, score, lives, items = 'PLAYING', 0, 5, []
                start_ticks, total_paused_time = pygame.time.get_ticks(), 0
                pygame.time.delay(200)
            if draw_button("QUIT GAME", WIDTH//2 - 110, 380, 220, 60, RED, (255, 100, 100)):
                running = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT: running = False

        else:
            # วาดสายพาน
            pygame.draw.rect(screen, (80, 80, 80), (0, 335, WIDTH, 15))
            # วาดถังขยะทั้ง 4 ใบ
            for b in bins:
                pygame.draw.rect(screen, b["color"], b["rect"], border_top_left_radius=15, border_top_right_radius=15)
                pygame.draw.rect(screen, BLACK, b["rect"], 3, border_top_left_radius=15, border_top_right_radius=15)
                label = SMALL_FONT.render(b["label"], True, BLACK)
                screen.blit(label, (b["rect"].centerx - label.get_width()//2, b["rect"].y + 45))

            if state == 'PLAYING':
                seconds_passed = (pygame.time.get_ticks() - start_ticks - total_paused_time) // 1000
                if draw_button("||", WIDTH - 60, 20, 40, 40, DARK_GRAY, GRAY):
                    state, pause_start_tick = 'PAUSED', pygame.time.get_ticks()
                    pygame.time.delay(200)

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
                    if item.rect.x > WIDTH: items.remove(item); lives -= 1

                screen.blit(FONT.render(f"SCORE: {score}", True, WHITE), (20, 20))
                screen.blit(FONT.render(f"LIVES: {lives}", True, RED), (20, 60))
                time_txt = FONT.render(f"TIME: {seconds_passed}s", True, YELLOW)
                screen.blit(time_txt, time_txt.get_rect(center=(WIDTH//2, 40)))
                if lives <= 0: state, final_time = 'GAME_OVER', seconds_passed

            elif state == 'PAUSED':
                for item in items: item.draw()
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 150))
                screen.blit(overlay, (0,0))
                pygame.draw.rect(screen, DARK_GRAY, (WIDTH//2-150, 180, 300, 240), border_radius=20)
                txt = FONT.render("PAUSED", True, WHITE)
                screen.blit(txt, (WIDTH//2 - txt.get_width()//2, 210))
                if draw_button("RESUME", WIDTH//2-100, 270, 200, 50, GREEN, (70, 230, 70)):
                    total_paused_time += pygame.time.get_ticks() - pause_start_tick
                    state = 'PLAYING'; pygame.time.delay(200)
                if draw_button("MENU", WIDTH//2-100, 340, 200, 50, BLUE, (100, 100, 255)):
                    state = 'START_MENU'; pygame.time.delay(200)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT: running = False

            elif state == 'GAME_OVER':
                for item in items: item.draw()
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                overlay.fill((100, 0, 0, 150))
                screen.blit(overlay, (0,0))
                pygame.draw.rect(screen, WHITE, (WIDTH//2-200, 120, 400, 360), border_radius=20)
                title = FONT.render("GAME OVER", True, RED)
                screen.blit(title, (WIDTH//2 - title.get_width()//2, 160))
                screen.blit(FONT.render(f"Final Score: {score}", True, BLACK), (WIDTH//2-100, 230))
                screen.blit(FONT.render(f"Time: {final_time}s", True, BLACK), (WIDTH//2-60, 280))
                if draw_button("RESTART", WIDTH//2-160, 360, 140, 50, GREEN, (70, 230, 70)):
                    score, lives, items, total_paused_time = 0, 5, [], 0
                    start_ticks = pygame.time.get_ticks()
                    state = 'PLAYING'; pygame.time.delay(200)
                if draw_button("MENU", WIDTH//2+20, 360, 140, 50, BLUE, (100, 100, 255)):
                    state = 'START_MENU'; pygame.time.delay(200)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT: running = False

        pygame.display.flip()
        clock.tick(60)
    pygame.quit()

if __name__ == "__main__":
    main()
    