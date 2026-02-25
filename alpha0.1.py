import pygame
import random

# --- 1. การตั้งค่าพื้นฐาน (Setup) ---
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sorting Master - เกมแยกขยะสายพาน")

# สีที่ใช้ในเกม
WHITE  = (255, 255, 255)
BLACK  = (0, 0, 0)
GRAY   = (150, 150, 150)
RED    = (200, 50, 50)
GREEN  = (50, 200, 50)  # ขยะเปียก
BLUE   = (50, 50, 200)   # รีไซเคิล
YELLOW = (220, 220, 50) # ขยะทั่วไป
LIGHT_BG = (240, 240, 240)

# ฟอนต์
FONT = pygame.font.SysFont("Arial", 32, bold=True)
SMALL_FONT = pygame.font.SysFont("Arial", 24)

# ประเภทขยะ
TYPES = ["WET", "RECYCLE", "GENERAL"]

# --- 2. คลาสขยะ (Garbage Class) ---
class Garbage:
    def __init__(self):
        self.type = random.choice(TYPES)
        # เริ่มต้นนอกจอฝั่งซ้าย (x = -60) และอยู่ระดับกลางหน้าจอ
        self.rect = pygame.Rect(-60, HEIGHT // 2 - 30, 60, 60)
        self.dragging = False
        self.speed = random.uniform(2.0, 4.0) # สุ่มความเร็วขยะแต่ละชิ้น
        
        # กำหนดสีตามประเภท (หากมีรูปภาพให้ใช้ pygame.image.load แทน)
        if self.type == "WET": self.color = GREEN
        elif self.type == "RECYCLE": self.color = BLUE
        else: self.color = YELLOW

    def move(self):
        # ถ้าไม่ได้โดนลาก ให้เลื่อนไปทางขวาตามสายพาน
        if not self.dragging:
            self.rect.x += self.speed

    def draw(self):
        pygame.draw.rect(screen, self.color, self.rect, border_radius=8)
        pygame.draw.rect(screen, BLACK, self.rect, 2, border_radius=8) # เส้นขอบ
        # วาดสัญลักษณ์ตัวย่อไว้บนขยะ
        label = SMALL_FONT.render(self.type[0], True, WHITE)
        screen.blit(label, (self.rect.x + 20, self.rect.y + 15))

# --- 3. ข้อมูลถังขยะ (Bins) ---
bins = [
    {"type": "WET", "rect": pygame.Rect(100, 450, 150, 110), "color": GREEN, "label": "WET"},
    {"type": "RECYCLE", "rect": pygame.Rect(325, 450, 150, 110), "color": BLUE, "label": "RECYCLE"},
    {"type": "GENERAL", "rect": pygame.Rect(550, 450, 150, 110), "color": YELLOW, "label": "GENERAL"},
]

# --- 4. ฟังก์ชันหลัก (Main Function) ---
def main():
    clock = pygame.time.Clock()
    score = 0
    lives = 5
    items = []
    active_item = None
    
    # ตัวจับเวลา
    start_ticks = pygame.time.get_ticks()
    time_limit = 60 # จำกัดเวลา 60 วินาที

    # Event สำหรับสร้างขยะใหม่ทุกๆ 1.2 วินาที
    SPAWN_EVENT = pygame.USEREVENT + 1
    pygame.time.set_timer(SPAWN_EVENT, 1200)

    running = True
    while running:
        screen.fill(LIGHT_BG)
        
        # คำนวณเวลาที่เหลือ
        seconds_passed = (pygame.time.get_ticks() - start_ticks) // 1000
        time_left = max(0, time_limit - seconds_passed)

        # วาดสายพาน (Conveyor Belt)
        pygame.draw.rect(screen, GRAY, (0, HEIGHT // 2 - 10, WIDTH, 20))
        
        # วาดถังขยะ
        for b in bins:
            pygame.draw.rect(screen, b["color"], b["rect"], border_top_left_radius=10, border_top_right_radius=10)
            pygame.draw.rect(screen, BLACK, b["rect"], 3, border_top_left_radius=10, border_top_right_radius=10)
            label = FONT.render(b["label"], True, BLACK)
            screen.blit(label, (b["rect"].centerx - label.get_width()//2, b["rect"].y + 35))

        # --- การจัดการ Event ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

            if event.type == SPAWN_EVENT:
                items.append(Garbage())

            if event.type == pygame.MOUSEBUTTONDOWN:
                # ตรวจเช็คว่าคลิกโดนขยะตัวไหน (เช็คจากตัวใหม่ไปเก่า)
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
                            if b["type"] == active_item.type:
                                score += 10
                            else:
                                score = max(0, score - 5)
                                lives -= 1
                            items.remove(active_item)
                            hit_bin = True
                            break
                    
                    if not hit_bin:
                        active_item.dragging = False
                    active_item = None

            if event.type == pygame.MOUSEMOTION:
                if active_item and active_item.dragging:
                    active_item.rect.center = event.pos

        # --- อัปเดตตรรกะเกม ---
        for item in items[:]:
            item.move()
            item.draw()
            # ถ้าขยะหลุดขอบจอขวา
            if item.rect.x > WIDTH:
                items.remove(item)
                lives -= 1

        # --- แสดงผล UI ---
        # คะแนน (ซ้าย)
        score_txt = FONT.render(f"SCORE: {score}", True, BLACK)
        screen.blit(score_txt, (20, 20))
        
        # พลังชีวิต (ขวา)
        lives_txt = FONT.render(f"LIVES: {lives}", True, RED)
        screen.blit(lives_txt, (WIDTH - 160, 20))
        
        # ตัวนับเวลา (บนกลาง)
        time_txt = FONT.render(f"TIME: {time_left}s", True, BLUE)
        time_rect = time_txt.get_rect(center=(WIDTH // 2, 35))
        screen.blit(time_txt, time_rect)

        # --- ตรวจสอบเงื่อนไขจบเกม ---
        if lives <= 0 or time_left <= 0:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((255, 255, 255, 200)) # พื้นหลังโปร่งแสง
            screen.blit(overlay, (0,0))
            
            reason = "TIME UP!" if time_left <= 0 else "GAME OVER!"
            end_txt = FONT.render(f"{reason} Final Score: {score}", True, BLACK)
            restart_txt = SMALL_FONT.render("Press 'R' to Restart or 'ESC' to Quit", True, BLACK)
            
            screen.blit(end_txt, (WIDTH//2 - end_txt.get_width()//2, HEIGHT//2 - 40))
            screen.blit(restart_txt, (WIDTH//2 - restart_txt.get_width()//2, HEIGHT//2 + 20))
            
            pygame.display.flip()
            
            # ลูปค้างหน้าจอจบเกม
            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit(); return
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_r:
                            main(); return
                        if event.key == pygame.K_ESCAPE:
                            pygame.quit(); return

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()