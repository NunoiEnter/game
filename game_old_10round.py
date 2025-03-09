import pygame
import random
import sys
import os

# เริ่มต้น pygame
pygame.init()

# ตั้งค่าหน้าจอ
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chicken Coin Runner")

# โหลดฟอนต์
if os.path.exists("THSarabunNew.ttf"):
    font = pygame.font.Font("THSarabunNew.ttf", 32)
    small_font = pygame.font.Font("THSarabunNew.ttf", 24)
else:
    font = pygame.font.SysFont(None, 32)
    small_font = pygame.font.SysFont(None, 24)

# สี
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
SKY_BLUE = (135, 206, 235)

# โหลดรูปภาพ
try:
    chicken_img = pygame.image.load("chicken.png")
    chicken_img = pygame.transform.scale(chicken_img, (50, 50))
    coin_img = pygame.image.load("coin.png")
    coin_img = pygame.transform.scale(coin_img, (30, 30))
except pygame.error:
    # สร้างรูปทดแทนถ้าไม่มีไฟล์
    chicken_img = pygame.Surface((50, 50), pygame.SRCALPHA)
    pygame.draw.circle(chicken_img, (255, 255, 0), (25, 25), 25)
    coin_img = pygame.Surface((30, 30), pygame.SRCALPHA)
    pygame.draw.circle(coin_img, (255, 215, 0), (15, 15), 15)

# คำถามและคำตอบ
questions = [
    {
        "question": "การบรรจุชิดที่สุดแบบลูกบาศก์ ชนิดไหนบรรจุได้ชิดที่สุด",
        "choices": ["1.) ccp", "2.) hcp", "3.) fcc"],
        "answer": 0
    },
    {
        "question": "log 10 มีค่าเท่าไหร่",
        "choices": ["1.) 10", "2.) 533577755", "3.) 1"],
        "answer": 2
    },
    {
        "question": "แนวคิด สิ่งมีชีวิตเกิดจากสิ่งไม่มีชีวิต เรียกว่าอะไร",
        "choices": ["1.) special creation", "2.) Spontaneous generation", "3.) Cosmozonic creation"],
        "answer": 1
    }
]

# คลาสไก่
class Chicken:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT - 100
        self.width = 50
        self.height = 50
        self.speed = 10
        self.lanes = [WIDTH // 4, WIDTH // 2, 3 * WIDTH // 4]
        self.current_lane = 1

    def move(self, direction):
        if direction == "left" and self.current_lane > 0:
            self.current_lane -= 1
        elif direction == "right" and self.current_lane < 2:
            self.current_lane += 1
        self.x = self.lanes[self.current_lane]

    def draw(self):
        screen.blit(chicken_img, (self.x - self.width // 2, self.y - self.height // 2))

    def get_rect(self):
        return pygame.Rect(self.x - self.width // 2, self.y - self.height // 2, self.width, self.height)

# คลาสเหรียญ
class Coin:
    def __init__(self):
        self.lanes = [WIDTH // 4, WIDTH // 2, 3 * WIDTH // 4]
        self.x = random.choice(self.lanes)
        self.y = -30
        self.width = 30
        self.height = 30
        self.speed = 5

    def update(self):
        self.y += self.speed
        return self.y > HEIGHT

    def draw(self):
        screen.blit(coin_img, (self.x - self.width // 2, self.y - self.height // 2))

    def get_rect(self):
        return pygame.Rect(self.x - self.width // 2, self.y - self.height // 2, self.width, self.height)

# ฟังก์ชันแสดงข้อความ
def draw_text(text, font, color, x, y, centered=False):
    text_surface = font.render(text, True, color)
    if centered:
        text_rect = text_surface.get_rect(center=(x, y))
    else:
        text_rect = text_surface.get_rect(topleft=(x, y))
    screen.blit(text_surface, text_rect)

# ฟังก์ชันแสดงคำถาม
def show_question(question_data, remaining_time, bonus_time):
    total_time = 30 + bonus_time
    
    # วาดพื้นหลัง
    screen.fill(SKY_BLUE)
    
    # วาดคำถาม
    draw_text(question_data["question"], font, BLACK, WIDTH // 2, 100, True)
    
    # วาดตัวเลือก
    for i, choice in enumerate(question_data["choices"]):
        y_pos = 200 + i * 80
        pygame.draw.rect(screen, WHITE, (150, y_pos - 30, WIDTH - 300, 60), border_radius=10)
        draw_text(choice, font, BLACK, WIDTH // 2, y_pos, True)
    
    # วาดเวลา
    draw_text(f"เวลา: {remaining_time:.1f} วินาที", font, BLACK, WIDTH // 2, 50, True)

# ฟังก์ชันแสดงหน้าจอแพ้
def show_game_over(coins_collected, questions_correct):
    screen.fill(SKY_BLUE)
    draw_text("Game Over!", font, RED, WIDTH // 2, HEIGHT // 3, True)
    
    multiplier = 0
    if questions_correct == 1:
        multiplier = 2
    elif questions_correct == 2:
        multiplier = 4
    elif questions_correct == 3:
        multiplier = 6
    
    final_score = coins_collected * multiplier if multiplier > 0 else coins_collected
    
    draw_text(f"เก็บได้: {coins_collected} เหรียญ", font, BLACK, WIDTH // 2, HEIGHT // 2 - 30, True)
    draw_text(f"ตอบถูก: {questions_correct} ข้อ (x{multiplier if multiplier > 0 else 1})", font, BLACK, WIDTH // 2, HEIGHT // 2 + 10, True)
    draw_text(f"คะแนนสุดท้าย: {final_score}", font, BLACK, WIDTH // 2, HEIGHT // 2 + 50, True)
    draw_text("กด SPACE เพื่อเล่นใหม่", font, BLACK, WIDTH // 2, HEIGHT // 2 + 100, True)
    draw_text("กด Q เพื่อออกจากเกม", font, BLACK, WIDTH // 2, HEIGHT // 2 + 140, True)

# ฟังก์ชันถามยืนยันการออกจากเกม
def confirm_exit():
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 128))
    screen.blit(overlay, (0, 0))
    
    pygame.draw.rect(screen, WHITE, (WIDTH // 4, HEIGHT // 3, WIDTH // 2, HEIGHT // 3), border_radius=20)
    draw_text("คุณต้องการออกจากเกมหรือไม่?", font, BLACK, WIDTH // 2, HEIGHT // 2 - 30, True)
    draw_text("Y - ใช่", font, BLACK, WIDTH // 2, HEIGHT // 2 + 20, True)
    draw_text("N - ไม่", font, BLACK, WIDTH // 2, HEIGHT // 2 + 60, True)
    
    pygame.display.flip()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_y:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_n:
                    return

def main():
    clock = pygame.time.Clock()
    chicken = Chicken()
    coins = []
    coins_collected = 0
    spawn_timer = 0
    game_state = "playing"  # playing, question, game_over
    current_question = 0
    question_time = 0
    bonus_time = 0
    questions_correct = 0
    special_coins = 0  # นับเหรียญพิเศษทุก 20 เหรียญ
    
    running = True
    while running:
        # จัดการอินพุต
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    confirm_exit()
                
                if game_state == "playing":
                    if event.key == pygame.K_LEFT:
                        chicken.move("left")
                    elif event.key == pygame.K_RIGHT:
                        chicken.move("right")
                
                elif game_state == "question":
                    if event.key in [pygame.K_1, pygame.K_KP1] or event.key == pygame.K_a:
                        if questions[current_question]["answer"] == 0:
                            questions_correct += 1
                            game_state = "playing"
                            current_question += 1
                            coins_collected = 0
                            special_coins = 0
                        else:
                            game_state = "game_over"
                    
                    elif event.key in [pygame.K_2, pygame.K_KP2] or event.key == pygame.K_b:
                        if questions[current_question]["answer"] == 1:
                            questions_correct += 1
                            game_state = "playing"
                            current_question += 1
                            coins_collected = 0
                            special_coins = 0
                        else:
                            game_state = "game_over"
                    
                    elif event.key in [pygame.K_3, pygame.K_KP3] or event.key == pygame.K_c:
                        if questions[current_question]["answer"] == 2:
                            questions_correct += 1
                            game_state = "playing"
                            current_question += 1
                            coins_collected = 0
                            special_coins = 0
                        else:
                            game_state = "game_over"
                
                elif game_state == "game_over":
                    if event.key == pygame.K_SPACE:
                        # เริ่มเกมใหม่
                        chicken = Chicken()
                        coins = []
                        coins_collected = 0
                        spawn_timer = 0
                        game_state = "playing"
                        current_question = 0
                        questions_correct = 0
                        special_coins = 0
                        bonus_time = 0
        
        # อัปเดตเกม
        if game_state == "playing":
            # สุ่มสร้างเหรียญ
            spawn_timer += 1
            if spawn_timer >= 30:  # ทุก 0.5 วินาที (ที่ 60 FPS)
                coins.append(Coin())
                spawn_timer = 0
            
            # อัปเดตเหรียญ
            for coin in coins[:]:
                if coin.update():
                    coins.remove(coin)
                elif chicken.get_rect().colliderect(coin.get_rect()):
                    coins.remove(coin)
                    coins_collected += 1
                    special_coins += 1
                    
                    # ทุก 20 เหรียญได้โบนัสเวลา 5 วินาที
                    if special_coins >= 2:
                        bonus_time += 5
                        special_coins = 0
            
            # ตรวจสอบว่าเก็บครบ 100 เหรียญหรือยัง
            if coins_collected >= 10:
                game_state = "question"
                question_time = 30 + bonus_time  # เวลาตอบคำถาม 30 วินาที + โบนัส
            
            # วาดเกม
            screen.fill(SKY_BLUE)
            chicken.draw()
            for coin in coins:
                coin.draw()
            
            # แสดงข้อมูล
            draw_text(f"เหรียญ: {coins_collected}/10", font, BLACK, 10, 10)
            draw_text(f"ตอบถูก: {questions_correct}/3", font, BLACK, 10, 50)
            draw_text(f"โบนัสเวลา: +{bonus_time}s", font, GREEN, 10, 90)
            
            if current_question < 3:
                draw_text(f"คำถามต่อไป: {current_question + 1}", font, BLACK, WIDTH - 200, 10)
        
        elif game_state == "question":
            question_time -= 1/60  # ลดเวลาลง (60 FPS)
            
            if question_time <= 0:
                game_state = "game_over"
            
            show_question(questions[current_question], question_time, bonus_time)
        
        elif game_state == "game_over":
            if questions_correct >= 3:  # ชนะเกม
                show_game_over(10, questions_correct)  # ถ้าตอบครบ 3 ข้อ จะมีเหรียญครบ 300 เหรียญ (100 * 3)
            else:
                show_game_over(coins_collected, questions_correct)
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()