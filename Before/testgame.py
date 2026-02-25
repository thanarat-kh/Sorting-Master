import pygame
import random

# ตั้งค่าเริ่มต้น
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sorting Master - เกมแยกขยะ")

# สี
WHITE = (255, 255, 255)
GREEN = (50, 200, 50)  # ขยะเปียก
BLUE = (50, 50, 200)   # รีไซเคิล
YELLOW = (200, 200, 50) # ขยะทั่วไป

# ประเภทขยะ
TYPES = ["WET", "RECYCLE", "GENERAL"]

class Garbage:
    def __init__(self):
        self.type = random.choice(TYPES)
        self.rect = pygame.Rect(random.randint(100, 700), 50, 50, 50)
        self.dragging = False
        # กำหนดสีตามประเภท (ในเกมจริงให้ใช้รูปภาพ)
        if self.type == "WET": self.color = GREEN
        elif self.type == "RECYCLE": self.color = BLUE
        else: self.color = YELLOW

    def draw(self):
        pygame.draw.rect(screen, self.color, self.rect)

# สร้างถังขยะ (Bins)
bins = [
    {"type": "WET", "rect": pygame.Rect(100, 450, 150, 100), "color": GREEN, "label": "WET"},
    {"type": "RECYCLE", "rect": pygame.Rect(325, 450, 150, 100), "color": BLUE, "label": "RECYCLE"},
    {"type": "GENERAL", "rect": pygame.Rect(550, 450, 150, 100), "color": YELLOW, "label": "GENERAL"},
]

def main():
    clock = pygame.time.Clock()
    score = 0
    items = [Garbage() for _ in range(3)] # เริ่มต้นมีขยะ 3 ชิ้น
    active_item = None
    font = pygame.font.SysFont("Arial", 30)

    running = True
    while running:
        screen.fill(WHITE)
        
        # วาดถังขยะ
        for b in bins:
            pygame.draw.rect(screen, b["color"], b["rect"])
            label = font.render(b["label"], True, (0, 0, 0))
            screen.blit(label, (b["rect"].x + 20, b["rect"].y + 35))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # เช็คว่าคลิกโดนขยะชิ้นไหน
                for item in items:
                    if item.rect.collidepoint(event.pos):
                        item.dragging = True
                        active_item = item
                        break
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if active_item:
                    correct = False
                    # เช็คว่าวางลงในถังที่ถูกต้องหรือไม่
                    for b in bins:
                        if b["rect"].colliderect(active_item.rect):
                            if b["type"] == active_item.type:
                                score += 10
                                items.remove(active_item)
                                items.append(Garbage()) # เพิ่มขยะใหม่
                                correct = True
                            else:
                                score -= 5 # ลงผิดถังโดนหักคะแนน
                    
                    if not correct:
                        # ถ้าวางไม่ลงถัง ให้กลับไปที่เดิม (หรืออยู่ที่เดิม)
                        active_item.dragging = False
                    active_item = None

            elif event.type == pygame.MOUSEMOTION:
                if active_item and active_item.dragging:
                    active_item.rect.center = event.pos

        # วาดขยะทุกชิ้น
        for item in items:
            item.draw()

        # แสดงคะแนน
        score_text = font.render(f"Score: {score}", True, (0, 0, 0))
        screen.blit(score_text, (20, 20))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()