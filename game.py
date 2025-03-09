import pygame
import sys
import random
import os

# Initialize pygame
pygame.init()
pygame.font.init()

# ค่าคงที่ของเกม
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRAVITY = 0.75
GROUND_HEIGHT = 500
COIN_COUNT = 100
QUESTIONS_TO_WIN = 3
QUESTION_TIME = 30 * 1000  # 30 วินาที
BONUS_TIME = 5 * 1000  # 5 วินาที 
COINS_FOR_BONUS = 20
LEVEL_WIDTH = 5000  # ความกว้างของด่าน

# สี
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
LIGHT_BLUE = (173, 216, 230)
BROWN = (139, 69, 19)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("ไก่น้อยเก็บเหรียญ")
clock = pygame.time.Clock()

try:
    font = pygame.font.Font("THSarabunNew.ttf", 32)
    big_font = pygame.font.Font("THSarabunNew.ttf", 48)
except:
    font = pygame.font.SysFont(None, 32)
    big_font = pygame.font.SysFont(None, 48)

try:
    chicken_img = pygame.image.load("chicken.png")
    chicken_img = pygame.transform.scale(chicken_img, (50, 50))
    coin_img = pygame.image.load("coin.png")
    coin_img = pygame.transform.scale(coin_img, (30, 30))
except:
    chicken_img = pygame.Surface((50, 50), pygame.SRCALPHA)
    pygame.draw.circle(chicken_img, (255, 255, 0), (25, 25), 25)
    coin_img = pygame.Surface((30, 30), pygame.SRCALPHA)
    pygame.draw.circle(coin_img, YELLOW, (15, 15), 15)

questions = [
    {
        "question": "การบรรจุชิดที่สุดแบบลูกบาศก์ ชนิดไหนบรรจุได้ชิดที่สุด",
        "choices": ["1.) ccp", "2.) hcp", "3.) fcc"],
        "correct": 0  
    },
    {
        "question": "log 10 มีค่าเท่าไหร่",
        "choices": ["1.) 10", "2.) 533577755", "3.) 1"],
        "correct": 2  
    },
    {
        "question": "แนวคิด สิ่งมีชีวิตเกิดจากสิ่งไม่มีชีวิต เรียกว่าอะไร",
        "choices": ["1.) special creation", "2.) Spontaneous generation", "3.) Cosmozonic creation"],
        "correct": 1  
    }
]

# คลาสตัวละครไก่
class Chicken:
    def __init__(self):
        self.x = 100
        self.y = GROUND_HEIGHT - 50
        self.vel_x = 5 
        self.vel_y = 0
        self.jumping = False
        self.on_ground = True
        self.image = chicken_img
        self.rect = self.image.get_rect(center=(self.x, self.y))
        self.world_x = 0 
        
    def update(self, keys, platforms):
        move_x = 0
        
        # การเคลื่อนที่ซ้าย-ขวา
        if keys[pygame.K_LEFT]:
            move_x = -self.vel_x
        if keys[pygame.K_RIGHT]:
            move_x = self.vel_x
            
        # อัพเดทตำแหน่งในโลก
        self.world_x += move_x
        self.world_x = max(0, min(self.world_x, LEVEL_WIDTH - SCREEN_WIDTH // 2))
        
        # กำหนดตำแหน่งบนหน้าจอ
        if self.world_x < SCREEN_WIDTH // 2:
            self.x = self.world_x
        elif self.world_x > LEVEL_WIDTH - SCREEN_WIDTH // 2:
            self.x = SCREEN_WIDTH - (LEVEL_WIDTH - self.world_x)
        else:
            self.x = SCREEN_WIDTH // 2
            
        # แรงโน้มถ่วง
        self.vel_y += GRAVITY
        self.y += self.vel_y
        
        # ตรวจสอบการชนกับพื้น
        self.on_ground = False
        for platform in platforms:
            rel_x = platform.x - (self.world_x - self.x)
            if (self.y + 25 >= platform.y and
                self.y + 25 <= platform.y + 10 and
                self.x + 25 >= rel_x and
                self.x - 25 <= rel_x + platform.width):
                self.y = platform.y - 25
                self.vel_y = 0
                self.jumping = False
                self.on_ground = True
                break
        
        # ถ้าตกพ้นพื้น
        if self.y > SCREEN_HEIGHT:
            return False
                
        # อัพเดทตำแหน่ง
        self.rect.center = (self.x, self.y)
        return True
        
    def jump(self):
        if self.on_ground:
            self.vel_y = -15
            self.jumping = True
            self.on_ground = False
            
    def draw(self, screen):
        screen.blit(self.image, self.rect)

# คลาสเหรียญ
class Coin:
    def __init__(self, world_x, y):
        self.world_x = world_x
        self.y = y
        self.image = coin_img
        self.rect = self.image.get_rect(center=(0, self.y))  # x จะคำนวณในแต่ละเฟรม
        self.collected = False
        
    def update(self, camera_x):
        rel_x = self.world_x - camera_x
        if 0 <= rel_x <= SCREEN_WIDTH:
            self.rect.centerx = rel_x
            return True
        return False
        
    def draw(self, screen):
        screen.blit(self.image, self.rect)

# คลาสแพลตฟอร์ม
class Platform:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
    def update(self, camera_x):
        rel_x = self.x - camera_x
        if rel_x + self.width >= 0 and rel_x <= SCREEN_WIDTH:
            self.rect.x = rel_x
            self.rect.y = self.y
            return True
        return False
        
    def draw(self, screen):
        rel_x = self.rect.x
        pygame.draw.rect(screen, BROWN, (rel_x, self.y, self.width, self.height))

# คลาสอุปสรรค
class Obstacle:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
    def update(self, camera_x):
        rel_x = self.x - camera_x
        if rel_x + self.width >= 0 and rel_x <= SCREEN_WIDTH:
            self.rect.x = rel_x
            self.rect.y = self.y
            return True
        return False
        
    def draw(self, screen):
        rel_x = self.rect.x
        pygame.draw.rect(screen, RED, (rel_x, self.y, self.width, self.height))

# สร้างด่าน
def create_level():
    platforms = []
    coins = []
    obstacles = []
    
    # สร้างพื้นหลัก
    ground_segments = []
    segment_width = 500
    gap_width = 200
    
    x = 0
    while x < LEVEL_WIDTH:
        ground_segments.append((x, x + segment_width))
        x += segment_width + gap_width
    
    for start, end in ground_segments:
        platforms.append(Platform(start, GROUND_HEIGHT, end - start, 100))
    
    # สร้างแพลตฟอร์มเพิ่มเติม
    num_platforms = 30
    for _ in range(num_platforms):
        x = random.randint(200, LEVEL_WIDTH - 200)
        y = random.randint(300, GROUND_HEIGHT - 50)
        width = random.randint(50, 200)
        platforms.append(Platform(x, y, width, 20))
    
    # # สร้างอุปสรรค
    # num_obstacles = 20
    # for _ in range(num_obstacles):
    #     x = random.randint(300, LEVEL_WIDTH - 300)
    #     y = random.randint(GROUND_HEIGHT - 100, GROUND_HEIGHT - 20)
    #     width = random.randint(30, 70)
    #     height = random.randint(30, 80)
    #     obstacles.append(Obstacle(x, y, width, height))
    
    # สร้างเหรียญ
    for _ in range(COIN_COUNT):
        # หาแพลตฟอร์มสุ่ม
        platform = random.choice(platforms)
        x = random.randint(int(platform.x), int(platform.x + platform.width - 30))
        y = platform.y - random.randint(40, 100)
        coins.append(Coin(x, y))
    
    # เพิ่มเหรียญบนทางตรง
    for segment_start, segment_end in ground_segments:
        for _ in range(5):
            x = random.randint(segment_start, segment_end - 30)
            y = GROUND_HEIGHT - random.randint(40, 120)
            coins.append(Coin(x, y))
    
    return platforms, coins, obstacles

# ฟังก์ชันหน้าคำถาม
def question_screen(question_index, bonus_time):
    question = questions[question_index]
    timer = QUESTION_TIME + bonus_time
    selected = None
    
    while timer > 0:
        current_time = pygame.time.get_ticks()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return ask_exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    if ask_exit():
                        return False
                elif event.key == pygame.K_1:
                    selected = 0
                elif event.key == pygame.K_2:
                    selected = 1
                elif event.key == pygame.K_3:
                    selected = 2
                elif event.key == pygame.K_RETURN and selected is not None:
                    return selected == question["correct"]
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                # ตรวจสอบว่าคลิกที่ตัวเลือกใด
                for i in range(3):
                    choice_rect = pygame.Rect(SCREEN_WIDTH // 2 - 200, 250 + i * 70, 400, 50)
                    if choice_rect.collidepoint(mouse_pos):
                        selected = i
                        return selected == question["correct"]
                    
        # วาดพื้นหลัง
        screen.fill(LIGHT_BLUE)
        
        # วาดคำถาม
        question_text = font.render(question["question"], True, BLACK)
        question_rect = question_text.get_rect(center=(SCREEN_WIDTH // 2, 150))
        screen.blit(question_text, question_rect)
        
        # วาดตัวเลือก
        for i, choice in enumerate(question["choices"]):
            choice_rect = pygame.Rect(SCREEN_WIDTH // 2 - 200, 250 + i * 70, 400, 50)
            color = BLUE if selected == i else WHITE
            pygame.draw.rect(screen, color, choice_rect)
            pygame.draw.rect(screen, BLACK, choice_rect, 2)
            
            choice_text = font.render(choice, True, BLACK)
            choice_text_rect = choice_text.get_rect(center=choice_rect.center)
            screen.blit(choice_text, choice_text_rect)
            
        # วาดเวลา
        time_left = max(0, timer - (pygame.time.get_ticks() - current_time))
        timer = time_left
        seconds_left = time_left // 1000
        time_text = font.render(f"เวลา: {seconds_left} วินาที", True, BLACK)
        time_rect = time_text.get_rect(topright=(SCREEN_WIDTH - 20, 20))
        screen.blit(time_text, time_rect)
        
        pygame.display.flip()
        clock.tick(60)
        
    # หมดเวลา
    return False

# ฟังก์ชันหน้าจบเกม
def game_over_screen(score, correct_answers):
    multiplier = 0
    if correct_answers == 1:
        multiplier = 2
    elif correct_answers == 2:
        multiplier = 4
    elif correct_answers == 3:
        multiplier = 6
        
    final_score = score * multiplier if multiplier > 0 else score
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return True
                elif event.key == pygame.K_q:
                    if ask_exit():
                        return False
        
        screen.fill(LIGHT_BLUE)
        
        if correct_answers == QUESTIONS_TO_WIN:
            title_text = big_font.render("ยินดีด้วย คุณชนะแล้ว!", True, GREEN)
        else:
            title_text = big_font.render("เสียใจด้วย คุณแพ้แล้ว", True, RED)
            
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
        screen.blit(title_text, title_rect)
        
        score_text = font.render(f"คะแนน: {score} x {multiplier} = {final_score}", True, BLACK)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(score_text, score_rect)
        
        instruction_text = font.render("กด ENTER เพื่อเล่นใหม่ หรือ Q เพื่อออก", True, BLACK)
        instruction_rect = instruction_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT * 2 // 3))
        screen.blit(instruction_text, instruction_rect)
        
        pygame.display.flip()
        clock.tick(60)

def ask_exit():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_y:
                    return True
                elif event.key == pygame.K_n:
                    return False
                
        screen.fill(LIGHT_BLUE)
        
        question_text = font.render("คุณต้องการออกจากเกมหรือไม่? (Y/N)", True, BLACK)
        question_rect = question_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(question_text, question_rect)
        
        pygame.display.flip()
        clock.tick(60)

# ฟังก์ชันหลัก
def main():
    while True:
        # เริ่มเกมใหม่
        chicken = Chicken()
        platforms, coins, obstacles = create_level()
        coins_collected = 0
        question_index = 0
        correct_answers = 0
        coins_collected_since_bonus = 0
        bonus_time = 0
        
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    if ask_exit():
                        return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP or event.key == pygame.K_SPACE:
                        chicken.jump()
                    elif event.key == pygame.K_q:
                        if ask_exit():
                            return
            
            # อัพเดทตัวละคร
            keys = pygame.key.get_pressed()
            if not chicken.update(keys, platforms):
                # ตกหลุม
                if game_over_screen(coins_collected, 0):
                    break  # เล่นใหม่
                else:
                    return  # ออกจากเกม
            
            # อัพเดทกล้อง
            camera_x = chicken.world_x - chicken.x
            
            # วาดพื้นหลัง
            screen.fill(LIGHT_BLUE)
            
            # วาดแพลตฟอร์ม
            visible_platforms = []
            for platform in platforms:
                if platform.update(camera_x):
                    visible_platforms.append(platform)
                    platform.draw(screen)
            
            # วาดอุปสรรค
            for obstacle in obstacles:
                if obstacle.update(camera_x):
                    obstacle.draw(screen)
                    
                    # ตรวจสอบการชนกับอุปสรรค
                    if chicken.rect.colliderect(obstacle.rect):
                        if game_over_screen(coins_collected, 0):
                            running = False
                            break  # เล่นใหม่
                        else:
                            return  # ออกจากเกม
            
            # อัพเดทและวาดเหรียญ
            coins_to_remove = []
            for coin in coins:
                if coin.update(camera_x):
                    coin.draw(screen)
                    
                    # ตรวจสอบการชนกับเหรียญ
                    if not coin.collected and chicken.rect.colliderect(coin.rect):
                        coin.collected = True
                        coins_collected += 1
                        coins_collected_since_bonus += 1
                        coins_to_remove.append(coin)
                        
                        # ตรวจสอบโบนัสเวลา
                        if coins_collected_since_bonus >= COINS_FOR_BONUS:
                            bonus_time += BONUS_TIME
                            coins_collected_since_bonus = 0
            
            # ลบเหรียญที่เก็บแล้ว
            for coin in coins_to_remove:
                coins.remove(coin)
            
            # วาดตัวละคร
            chicken.draw(screen)
            
            # ตรวจสอบว่าเก็บเหรียญครบหรือไม่
            if coins_collected >= COIN_COUNT:
                # แสดงคำถาม
                if question_screen(question_index, bonus_time):
                    # ตอบถูก
                    correct_answers += 1
                    question_index += 1
                    bonus_time = 0
                    
                    # ตรวจสอบว่าตอบคำถามครบหรือไม่
                    if question_index >= QUESTIONS_TO_WIN:
                        if game_over_screen(coins_collected, correct_answers):
                            break  # เล่นใหม่
                        else:
                            return  # ออกจากเกม
                    else:
                        # สร้างด่านใหม่
                        chicken = Chicken()
                        platforms, coins, obstacles = create_level()
                        coins_collected = 0
                        coins_collected_since_bonus = 0
                else:
                    # ตอบผิดหรือหมดเวลา
                    if game_over_screen(coins_collected, correct_answers):
                        break  # เล่นใหม่
                    else:
                        return  # ออกจากเกม
            
            # แสดงคะแนน
            score_text = font.render(f"เหรียญ: {coins_collected}/{COIN_COUNT}", True, BLACK)
            screen.blit(score_text, (20, 20))
            
            # แสดงโบนัสเวลา
            if bonus_time > 0:
                bonus_text = font.render(f"โบนัสเวลา: +{bonus_time // 1000} วินาที", True, BLACK)
                screen.blit(bonus_text, (20, 60))
            
            # แสดงคำถามที่ตอบถูก
            question_text = font.render(f"คำถามที่ตอบถูก: {correct_answers}/{QUESTIONS_TO_WIN}", True, BLACK)
            screen.blit(question_text, (SCREEN_WIDTH - 250, 20))
            
            pygame.display.flip()
            clock.tick(60)

if __name__ == "__main__":
    main()
    pygame.quit()
    sys.exit()