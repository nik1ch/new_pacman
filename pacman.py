import pygame
import copy
from board import boards

pygame.init()


WIDTH = 900
HEIGHT = 950
fps = 60

screen = pygame.display.set_mode([WIDTH, HEIGHT])
timer = pygame.time.Clock()

font = pygame.font.Font('freesansbold.ttf', 20)
level = copy.deepcopy(boards) #создание копии переменной boards
color = 'violet'


player_images = []
for i in range(1, 5):
    player_images.append(pygame.transform.scale(pygame.image.load(f'assets/player_images/{i}.png'), (45, 45))) # анимация

red_img = pygame.transform.scale(pygame.image.load(f'assets/ghost_images/red.png'), (45, 45))
pink_img = pygame.transform.scale(pygame.image.load(f'assets/ghost_images/pink.png'), (45, 45))
blue_img = pygame.transform.scale(pygame.image.load(f'assets/ghost_images/blue.png'), (45, 45))
orange_img = pygame.transform.scale(pygame.image.load(f'assets/ghost_images/orange.png'), (45, 45))
spooked_img = pygame.transform.scale(pygame.image.load(f'assets/ghost_images/powerup.png'), (45, 45))
dead_img = pygame.transform.scale(pygame.image.load(f'assets/ghost_images/dead.png'), (45, 45))

player_x = 450
player_y = 663

direction = 0 # направление

red_x = 56
red_y = 58
red_direction = 0

blue_x = 440
blue_y = 388
blue_direction = 2

pink_x = 440
pink_y = 438
pink_direction = 2

orange_x = 380
orange_y = 438
orange_direction = 2

counter = 0 # счетчик
flicker = False # мигание 

turns_allowed = [False, False, False, False] # повороты, вправо, влево, вверх, вниз
direction_command = 0
player_speed = 2
score = 0
powerup = False
power_counter = 0
eaten_ghost = [False, False, False, False]
targets = [(player_x, player_y), (player_x, player_y), (player_x, player_y), (player_x, player_y)]

red_dead = False
blue_dead = False
orange_dead = False
pink_dead = False

red_box = False
blue_box = False
orange_box = False
pink_box = False

moving = False # задержка в начале игры
ghost_speeds = [2, 2, 2, 2]
startup_counter = 0
lives = 3

game_over = False
game_won = False

def variables():
    global powerup, power_counter, startup_counter, player_x, player_y, direction, \
        direction_command, red_x, red_y, red_direction, blue_x, blue_y, blue_direction, \
        pink_x, pink_y, pink_direction, orange_x, orange_y, orange_direction, eaten_ghost, \
        red_dead, blue_dead, orange_dead, pink_dead
    powerup = False
    power_counter = 0
    startup_counter = 0
    player_x = 450
    player_y = 663
    direction = 0
    direction_command = 0
    red_x = 56
    red_y = 58
    red_direction = 0
    blue_x = 440
    blue_y = 388
    blue_direction = 2
    pink_x = 440
    pink_y = 438
    pink_direction = 2
    orange_x = 440
    orange_y = 438
    orange_direction = 2
    eaten_ghost = [False, False, False, False]
    red_dead = False
    blue_dead = False
    orange_dead = False
    pink_dead = False

    return powerup, power_counter, startup_counter, player_x, player_y, direction, \
        direction_command, red_x, red_y, red_direction, blue_x, blue_y, blue_direction, \
        pink_x, pink_y, pink_direction, orange_x, orange_y, orange_direction, eaten_ghost, \
        red_dead, blue_dead, orange_dead, pink_dead

class Ghost:
    def __init__(self, x_coord, y_coord, target, speed, img, direct, dead, box, id):
        self.x_pos = x_coord
        self.y_pos = y_coord
        self.center_x = self.x_pos + 22
        self.center_y = self.y_pos + 22
        self.target = target
        self.speed = speed
        self.img = img
        self.direction = direct
        self.dead = dead
        self.in_box = box
        self.id = id
        self.turns, self.in_box = self.check_collisions()
        self.rect = self.draw()

    def draw(self): # выбор картинки для призрака
        if (not powerup and not self.dead) or (eaten_ghost[self.id] and powerup and not self.dead):
            screen.blit(self.img, (self.x_pos, self.y_pos))
        elif powerup and not self.dead and not eaten_ghost[self.id]:
            screen.blit(spooked_img, (self.x_pos, self.y_pos))
        else:
            screen.blit(dead_img, (self.x_pos, self.y_pos))
        ghost_rect = pygame.rect.Rect((self.center_x - 18, self.center_y - 18), (30, 30))
        return ghost_rect

    def check_collisions(self): # проверка столкновений
        num1 = ((HEIGHT - 50) // 32)
        num2 = (WIDTH // 30)
        num3 = 15
        self.turns = [False, False, False, False] # справа, слева, сверху, снизу 
        if 0 < self.center_x // 30 < 29:
            if level[(self.center_y - num3) // num1][self.center_x // num2] == 9: # выход призрака за ворота
                self.turns[2] = True
            if level[self.center_y // num1][(self.center_x - num3) // num2] < 3 \
                    or (level[self.center_y // num1][(self.center_x - num3) // num2] == 9 and (
                    self.in_box or self.dead)): # столкновение слева
                self.turns[1] = True
            if level[self.center_y // num1][(self.center_x + num3) // num2] < 3 \
                    or (level[self.center_y // num1][(self.center_x + num3) // num2] == 9 and (
                    self.in_box or self.dead)): # столкновение справа
                self.turns[0] = True
            if level[(self.center_y + num3) // num1][self.center_x // num2] < 3 \
                    or (level[(self.center_y + num3) // num1][self.center_x // num2] == 9 and (
                    self.in_box or self.dead)): # столкновение снизу
                self.turns[3] = True
            if level[(self.center_y - num3) // num1][self.center_x // num2] < 3 \
                    or (level[(self.center_y - num3) // num1][self.center_x // num2] == 9 and (
                    self.in_box or self.dead)): # столкновение сверху
                self.turns[2] = True

            # проверка движения если призрак стоит на границе двух клеток и если призрак движется прямо сейчас вверх или вниз
            if self.direction == 2 or self.direction == 3:
                if 12 <= self.center_x % num2 <= 18:
                    if level[(self.center_y + num3) // num1][self.center_x // num2] < 3 \
                            or (level[(self.center_y + num3) // num1][self.center_x // num2] == 9 and (
                            self.in_box or self.dead)):
                        self.turns[3] = True # снизу
                    if level[(self.center_y - num3) // num1][self.center_x // num2] < 3 \
                            or (level[(self.center_y - num3) // num1][self.center_x // num2] == 9 and (
                            self.in_box or self.dead)):
                        self.turns[2] = True # сверху
                if 12 <= self.center_y % num1 <= 18:
                    if level[self.center_y // num1][(self.center_x - num2) // num2] < 3 \
                            or (level[self.center_y // num1][(self.center_x - num2) // num2] == 9 and (
                            self.in_box or self.dead)):
                        self.turns[1] = True # слева
                    if level[self.center_y // num1][(self.center_x + num2) // num2] < 3 \
                            or (level[self.center_y // num1][(self.center_x + num2) // num2] == 9 and (
                            self.in_box or self.dead)):
                        self.turns[0] = True # справа

            # проверка движения если призрак стоит на границе двух клеток и если призрак движется прямо сейчас вправо или влево
            if self.direction == 0 or self.direction == 1:
                if 12 <= self.center_x % num2 <= 18:
                    if level[(self.center_y + num3) // num1][self.center_x // num2] < 3 \
                            or (level[(self.center_y + num3) // num1][self.center_x // num2] == 9 and (
                            self.in_box or self.dead)):
                        self.turns[3] = True
                    if level[(self.center_y - num3) // num1][self.center_x // num2] < 3 \
                            or (level[(self.center_y - num3) // num1][self.center_x // num2] == 9 and (
                            self.in_box or self.dead)):
                        self.turns[2] = True
                if 12 <= self.center_y % num1 <= 18:
                    if level[self.center_y // num1][(self.center_x - num3) // num2] < 3 \
                            or (level[self.center_y // num1][(self.center_x - num3) // num2] == 9 and (
                            self.in_box or self.dead)):
                        self.turns[1] = True
                    if level[self.center_y // num1][(self.center_x + num3) // num2] < 3 \
                            or (level[self.center_y // num1][(self.center_x + num3) // num2] == 9 and (
                            self.in_box or self.dead)):
                        self.turns[0] = True
        else:
            self.turns[0] = True
            self.turns[1] = True
        if 350 < self.x_pos < 550 and 370 < self.y_pos < 480:
            self.in_box = True
        else:
            self.in_box = False
        return self.turns, self.in_box

    def move_ghost(self):
        # вправо, влево, вверх, вниз
        if self.direction == 0:
            if self.target[0] > self.x_pos and self.turns[0]:
                self.x_pos += self.speed
            elif not self.turns[0]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
            elif self.turns[0]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                if self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                else:
                    self.x_pos += self.speed
        elif self.direction == 1:
            if self.target[1] > self.y_pos and self.turns[3]:
                self.direction = 3
            elif self.target[0] < self.x_pos and self.turns[1]:
                self.x_pos -= self.speed
            elif not self.turns[1]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[1]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                if self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                else:
                    self.x_pos -= self.speed
        elif self.direction == 2:
            if self.target[0] < self.x_pos and self.turns[1]:
                self.direction = 1
                self.x_pos -= self.speed
            elif self.target[1] < self.y_pos and self.turns[2]:
                self.direction = 2
                self.y_pos -= self.speed
            elif not self.turns[2]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[2]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                else:
                    self.y_pos -= self.speed
        elif self.direction == 3:
            if self.target[1] > self.y_pos and self.turns[3]:
                self.y_pos += self.speed
            elif not self.turns[3]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[3]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                else:
                    self.y_pos += self.speed
        if self.x_pos < -30:
            self.x_pos = 900
        elif self.x_pos > 900:
            self.x_pos - 30
        return self.x_pos, self.y_pos, self.direction

def draw_elements(): # отрисовка фигур и текста
    score_text = font.render(f'Score: {score}', True,'white')
    screen.blit(score_text, (10, 920))
    if powerup:
        pygame.draw.circle(screen, 'blue', (140, 930), 15)
    for i in range(lives):
        screen.blit(pygame.transform.scale(player_images[0], (30, 30)), (650 + i * 40, 915))
    if game_over:
        pygame.draw.rect(screen, 'white', [50, 200, 800, 300],0, 10)
        pygame.draw.rect(screen, 'dark gray', [70, 220, 760, 260], 0, 10)
        gameover_text = font.render('Game over! Space bar to restart!', True, 'red')
        screen.blit(gameover_text, (280, 330))
    if game_won:
        pygame.draw.rect(screen, 'white', [50, 200, 800, 300],0, 10)
        pygame.draw.rect(screen, 'dark gray', [70, 220, 760, 260], 0, 10)
        gameover_text = font.render('Victory! Space bar for a new game!', True, 'green')
        screen.blit(gameover_text, (270, 330))

def check_collisions(scor, power, power_count, eaten_ghosts):
    num1 = (HEIGHT - 50) // 32
    num2 = WIDTH // 30
    if 0 < player_x < 870:
        if level[center_y // num1][center_x // num2] == 1: # если пакман стоит на монетке то он ее ест и плюс 10 к счету
            level[center_y // num1][center_x // num2] = 0
            scor += 10
        if level[center_y // num1][center_x // num2] == 2: # проверка на суперсилу
            level[center_y // num1][center_x // num2] = 0
            scor += 50
            power = True
            power_count = 0
            eaten_ghosts = [False, False, False, False]
    return scor, power, power_count, eaten_ghosts

def draw_board(): # прорисовка доски
    num1 = ((HEIGHT - 50) // 32)
    num2 = (WIDTH // 30)
    for i in range(len(level)):
        for j in range(len(level[i])):
            if level[i][j] == 1:
                pygame.draw.circle(screen, 'white', (j * num2 + (0.5 * num2), i * num1 + (0.5 * num1)), 4)
            if level[i][j] == 2 and not flicker:
                pygame.draw.circle(screen, 'white', (j * num2 + (0.5 * num2), i * num1 + (0.5 * num1)), 10)
            if level[i][j] == 3:
                pygame.draw.line(screen, color, (j * num2 + (0.5 * num2), i * num1),
                                 (j * num2 + (0.5 * num2), i * num1 + num1), 3)
            if level[i][j] == 4:
                pygame.draw.line(screen, color, (j * num2, i * num1 + (0.5 * num1)),
                                 (j * num2 + num2, i * num1 + (0.5 * num1)), 3)
            if level[i][j] == 5:
                pygame.draw.arc(screen, color, [(j * num2 - (num2 * 0.4)) - 2, (i * num1 + (0.5 * num1)), num2, num1],
                                0, 3.14 / 2, 3)
            if level[i][j] == 6:
                pygame.draw.arc(screen, color,
                                [(j * num2 + (num2 * 0.5)), (i * num1 + (0.5 * num1)), num2, num1], 3.14 / 2, 3.14, 3)
            if level[i][j] == 7:
                pygame.draw.arc(screen, color, [(j * num2 + (num2 * 0.5)), (i * num1 - (0.4 * num1)), num2, num1], 3.14,
                                3 * 3.14 / 2, 3)
            if level[i][j] == 8:
                pygame.draw.arc(screen, color,
                                [(j * num2 - (num2 * 0.4)) - 2, (i * num1 - (0.4 * num1)), num2, num1], 3 * 3.14 / 2,
                                2 * 3.14, 3)
            if level[i][j] == 9:
                pygame.draw.line(screen, 'white', (j * num2, i * num1 + (0.5 * num1)), 
                                 (j * num2 + num2, i * num1 + (0.5 * num1)), 3)

def draw_player():
    # 0 - вправо, 1 - влево, 2 - вверх, 3 - вниз
    if direction == 0:
        screen.blit(player_images[counter // 5], (player_x, player_y))
    elif direction == 1:
        screen.blit(pygame.transform.flip(player_images[counter // 5], True, False), (player_x, player_y))
    elif direction == 2:
        screen.blit(pygame.transform.rotate(player_images[counter // 5], 90), (player_x, player_y))
    elif direction == 3:
        screen.blit(pygame.transform.rotate(player_images[counter // 5], 270), (player_x, player_y))

def check_position(centerx, centery):
    turns = [False, False, False, False]
    num1 = (HEIGHT - 50) // 32
    num2 = (WIDTH // 30)
    num3 = 15
    if centerx // 30 < 29:
        if direction == 0:
            if level[centery // num1][(centerx - num3) // num2] < 3:
                turns[1] = True
        if direction == 1:
            if level[centery // num1][(centerx + num3) // num2] < 3:
                turns[0] = True
        if direction == 2:
            if level[(centery + num3) // num1][centerx // num2] < 3:
                turns[3] = True
        if direction == 3:
            if level[(centery - num3) // num1][centerx // num2] < 3:
                turns[2] = True

        if direction == 2 or direction == 3:
            if 12 <= centerx % num2 <= 18:
                if level[(centery + num3) // num1][centerx // num2] < 3:
                    turns[3] = True
                if level[(centery - num3) // num1][centerx // num2] < 3:
                    turns[2] = True
            if 12 <= centery % num1 <= 18:
                if level[centery // num1][(centerx - num2) // num2] < 3:
                    turns[1] = True
                if level[centery // num1][(centerx + num2) // num2] < 3:
                    turns[0] = True
        if direction == 0 or direction == 1:
            if 12 <= centerx % num2 <= 18:
                if level[(centery + num1) // num1][centerx // num2] < 3:
                    turns[3] = True
                if level[(centery - num1) // num1][centerx // num2] < 3:
                    turns[2] = True
            if 12 <= centery % num1 <= 18:
                if level[centery // num1][(centerx - num3) // num2] < 3:
                    turns[1] = True
                if level[centery // num1][(centerx + num3) // num2] < 3:
                    turns[0] = True
    else:
        turns[0] = True
        turns[1] = True

    return turns

def move_player(play_x, play_y):
    # вправо, влево, вверх, вниз
    if direction == 0 and turns_allowed[0]:
        play_x += player_speed
    elif direction == 1 and turns_allowed[1]:
        play_x -= player_speed
    if direction == 2 and turns_allowed[2]:
        play_y -= player_speed
    elif direction == 3 and turns_allowed[3]:
        play_y += player_speed
    return play_x, play_y

def get_targets(reds_x, reds_y, blues_x, blues_y, pinks_x, pinks_y, oranges_x, oranges_y): # преследование приведений 
    if player_x < 450:
        runaway_x = 900
    else:
        runaway_x = 0
    if player_y < 450:
        runaway_y = 900
    else:
        runaway_y = 0
    return_target = (380, 400)
    if powerup:
        if not red.dead and not eaten_ghost[0]:
            reds_target = (runaway_x, runaway_y)
        elif not red.dead and eaten_ghost[0]:
            if 340 < reds_x < 560 and 340 < reds_y < 500:
                reds_target = (400, 100)
            else:
                reds_target = (player_x, player_y)
        else:
            blues_target = return_target

        if not blue.dead and not eaten_ghost[1]:
            blues_target = (runaway_x, player_y)
        elif not blue.dead and eaten_ghost[1]:
            if 340 < blues_x < 560 and 340 < blues_y < 500:
                blues_target = (400, 100)
            else:
                blues_target = (player_x, player_y)
        else:
            blues_target = return_target
            
        if not pink.dead:
            pinks_target = (player_x, runaway_y)
        elif not pink.dead and eaten_ghost[2]:
            if 340 < pinks_x < 560 and 340 < pinks_y < 500:
                pinks_target = (400, 100)
            else:
                pinks_target = (player_x, player_y)
        else:
            pinks_target = return_target

        if not orange.dead and not eaten_ghost[3]:
            oranges_target = (450, 450)
        elif not orange.dead and eaten_ghost[3]:
            if 340 < oranges_x < 560 and 340 < oranges_y < 500:
                oranges_target = (400, 100)
            else:
                oranges_target = (player_x, player_y)
        else:
            oranges_target = return_target

    else:
        if not red.dead:
            if 340 < reds_x < 560 and 340 < reds_y < 500:
                reds_target = (400, 100)
            else:
                reds_target = (player_x, player_y)
        else:
            reds_target = return_target

        if not blue.dead:
            if 340 < blues_x < 560 and 340 < blues_y < 500:
                blues_target = (400, 100)
            else:
                blues_target = (player_x, player_y)
        else:
            blues_target = return_target

        if not pink.dead:
            if 340 < pinks_x < 560 and 340 < pinks_y < 500:
                pinks_target = (400, 100)
            else:
                pinks_target = (player_x, player_y)
        else:
            pinks_target = return_target

        if not orange.dead:
            if 340 < oranges_x < 560 and 340 < oranges_y < 500:
                oranges_target = (400, 100)
            else:
                oranges_target = (player_x, player_y)
        else:
            oranges_target = return_target

    return [reds_target, blues_target, pinks_target, oranges_target]


run = True
while run:
    timer.tick(fps)
    if counter < 19:
        counter += 1
        if counter > 3:
            flicker = False
    else:
        counter = 0
        flicker = True
    if powerup and power_counter < 600:
        power_counter += 1
    elif powerup and power_counter >= 600:
        power_counter = 0
        powerup = False
        eaten_ghost = [False, False, False, False]
    if startup_counter < 180 and not game_over and not game_won:
        moving = False
        startup_counter += 1
    else:
        moving = True

    screen.fill('black')
    draw_board()
    center_x = player_x + 23
    center_y = player_y + 24
    if powerup:
        ghost_speeds = [1, 1, 1, 1]
    else:
        ghost_speeds = [2, 2, 2, 2]
    if eaten_ghost[0]:
        ghost_speeds[0] = 2
    if eaten_ghost[1]:
        ghost_speeds[1] = 2
    if eaten_ghost[2]:
        ghost_speeds[2] = 2
    if eaten_ghost[3]:
        ghost_speeds[3] = 2
    if red_dead:
        ghost_speeds[0] = 4
    if blue_dead:
        ghost_speeds[1] = 4
    if pink_dead:
        ghost_speeds[2] = 4
    if orange_dead:
        ghost_speeds[3] = 4 

    game_won = True
    for i in range(len(level)):
        if 1 in level[i] or 2 in level[i]:
            game_won = False

    player_circle = pygame.draw.circle(screen, 'black', (center_x, center_y), 20, 2)
    draw_player()

    red = Ghost(red_x, red_y, targets[0], ghost_speeds[0], red_img, red_direction, red_dead, red_box, 0)
    blue = Ghost(blue_x, blue_y, targets[1], ghost_speeds[1], blue_img, blue_direction, blue_dead, blue_box, 1)
    pink = Ghost(pink_x, pink_y, targets[2], ghost_speeds[2], pink_img, pink_direction, pink_dead, pink_box, 2)
    orange = Ghost(orange_x, orange_y, targets[3], ghost_speeds[3], orange_img, orange_direction, orange_dead, orange_box, 3)

    draw_elements()
    targets = get_targets(red_x, red_y, blue_x, blue_y, pink_x, pink_y, orange_x, orange_y)

    turns_allowed = check_position(center_x, center_y)
    if moving:
        player_x, player_y = move_player(player_x, player_y)
        if not red_dead and not red.in_box:
            red_x, red_y, red_direction = red.move_ghost()
        else:
            red_x, red_y, red_direction = red.move_ghost()

        if not pink_dead and not pink.in_box:
            pink_x, pink_y, pink_direction = pink.move_ghost()
        else:
            pink_x, pink_y, pink_direction = pink.move_ghost()

        if not blue_dead and not blue.in_box:
            blue_x, blue_y, blue_direction = blue.move_ghost()
        else:
            blue_x, blue_y, blue_direction = blue.move_ghost()

        orange_x, orange_y, orange_direction = orange.move_ghost()

    score, powerup, power_counter, eaten_ghost = check_collisions(score, powerup, power_counter, eaten_ghost)

    if not powerup:
        if (player_circle.colliderect(red.rect) and not red.dead) or \
                (player_circle.colliderect(blue.rect) and not blue.dead) or \
                (player_circle.colliderect(pink.rect) and not pink.dead) or \
                (player_circle.colliderect(orange.rect) and not orange.dead):
            if lives > 0:
                lives -= 1
                powerup, power_counter, startup_counter, player_x, player_y, direction, \
                direction_command, red_x, red_y, red_direction, blue_x, blue_y, blue_direction, \
                pink_x, pink_y, pink_direction, orange_x, orange_y, orange_direction, eaten_ghost, \
                red_dead, blue_dead, orange_dead, pink_dead = variables()
            else:
                game_over = True
                moving = False
                startup_counter = 0
    if powerup and player_circle.colliderect(red.rect) and eaten_ghost[0] and not red.dead:
        if lives > 0:
            lives -= 1
            powerup, power_counter, startup_counter, player_x, player_y, direction, \
            direction_command, red_x, red_y, red_direction, blue_x, blue_y, blue_direction, \
            pink_x, pink_y, pink_direction, orange_x, orange_y, orange_direction, eaten_ghost, \
            red_dead, blue_dead, orange_dead, pink_dead = variables()
        else:
            game_over = True
            moving = False
            startup_counter = 0
    if powerup and player_circle.colliderect(blue.rect) and eaten_ghost[1] and not blue.dead:
        if lives > 0:
            powerup, power_counter, startup_counter, player_x, player_y, direction, \
            direction_command, red_x, red_y, red_direction, blue_x, blue_y, blue_direction, \
            pink_x, pink_y, pink_direction, orange_x, orange_y, orange_direction, eaten_ghost, \
            red_dead, blue_dead, orange_dead, pink_dead = variables()
        else:
            game_over = True
            moving = False
            startup_counter = 0
    if powerup and player_circle.colliderect(pink.rect) and eaten_ghost[2] and not pink.dead:
        if lives > 0:
            powerup, power_counter, startup_counter, player_x, player_y, direction, \
            direction_command, red_x, red_y, red_direction, blue_x, blue_y, blue_direction, \
            pink_x, pink_y, pink_direction, orange_x, orange_y, orange_direction, eaten_ghost, \
            red_dead, blue_dead, orange_dead, pink_dead = variables()
        else:
            game_over = True
            moving = False
            startup_counter = 0
    if powerup and player_circle.colliderect(orange.rect) and eaten_ghost[3] and not orange.dead:
        if lives > 0:
            powerup, power_counter, startup_counter, player_x, player_y, direction, \
            direction_command, red_x, red_y, red_direction, blue_x, blue_y, blue_direction, \
            pink_x, pink_y, pink_direction, orange_x, orange_y, orange_direction, eaten_ghost, \
            red_dead, blue_dead, orange_dead, pink_dead = variables()
        else:
            game_over = True
            moving = False
            startup_counter = 0

    if powerup and player_circle.colliderect(red.rect) and not red.dead and not eaten_ghost[0]:
        red_dead = True
        eaten_ghost[0] = True
        score += (2 ** eaten_ghost.count(True)) * 100
    if powerup and player_circle.colliderect(blue.rect) and not blue.dead and not eaten_ghost[1]:
        blue_dead = True
        eaten_ghost[1] = True
        score += (2 ** eaten_ghost.count(True)) * 100
    if powerup and player_circle.colliderect(pink.rect) and not pink.dead and not eaten_ghost[2]:
        pink_dead = True
        eaten_ghost[2] = True
        score += (2 ** eaten_ghost.count(True)) * 100
    if powerup and player_circle.colliderect(orange.rect) and not orange.dead and not eaten_ghost[3]:
        orange_dead = True
        eaten_ghost[3] = True
        score += (2 ** eaten_ghost.count(True)) * 100

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                direction_command = 0
            if event.key == pygame.K_LEFT:
                direction_command = 1
            if event.key == pygame.K_UP:
                direction_command = 2
            if event.key == pygame.K_DOWN:
                direction_command = 3
            if event.key == pygame.K_SPACE and (game_over or game_won):
                powerup, power_counter, startup_counter, player_x, player_y, direction, \
                direction_command, red_x, red_y, red_direction, blue_x, blue_y, blue_direction, \
                pink_x, pink_y, pink_direction, orange_x, orange_y, orange_direction, eaten_ghost, \
                red_dead, blue_dead, orange_dead, pink_dead = variables()
                score = 0
                lives = 3
                level = copy.deepcopy(boards)
                game_over = False
                game_won = False

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_RIGHT and direction_command == 0:
                direction_command = direction
            if event.key == pygame.K_LEFT and direction_command == 1:
                direction_command = direction
            if event.key == pygame.K_UP and direction_command == 2:
                direction_command = direction
            if event.key == pygame.K_DOWN and direction_command == 3:
                direction_command = direction

    if direction_command == 0 and turns_allowed[0]:
        direction = 0
    if direction_command == 1 and turns_allowed[1]:
        direction = 1
    if direction_command == 2 and turns_allowed[2]:
        direction = 2
    if direction_command == 3 and turns_allowed[3]:
        direction = 3

    if player_x > 900:
        player_x = -47
    elif player_x < -50:
        player_x = 897

    if red.in_box and red_dead:
        red_dead = False
    if blue.in_box and blue_dead:
        blue_dead = False
    if pink.in_box and pink_dead:
        pink_dead = False
    if orange.in_box and orange_dead:
        orange_dead = False

    pygame.display.flip()
pygame.quit()
