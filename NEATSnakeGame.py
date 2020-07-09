import pygame
import random
import neat
import os
import sys

pygame.init()

WIN_HEIGHT = 600
WIN_WIDTH = 800
SNAKE_BLOCK = 20
SNAKE_SPEED = 1000

KEY_UP = 0
KEY_DOWN = 1
KEY_LEFT = 2
KEY_RIGHT = 3

BLUE = (0, 0, 255)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 102)
GREEN = (0, 255, 0)

GEN = 0
random_snake = 0
DRAW_LINES = True

WIN = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
FONT_STYLE = pygame.font.SysFont("bahnschrift", 25)
SCORE_FONT = pygame.font.SysFont("comicsansms", 35)

pygame.display.set_caption("Snake Game")

class Snake:
    def __init__(self, food):
        self.x = WIN_WIDTH / 2
        self.y = WIN_HEIGHT / 2

        self.x_change = 0
        self.y_change = 0

        self.snake_length = 1
        self.snake_body = []

        self.last_dir = -1
        self.life_left = 200

        self.food = food
        self.dead = False

        self.old_dist = ((self.x-self.food.x)**2 + (self.y-self.food.y)**2)**0.5
        self.foods_eaten = 0

        self.direction_gone = []
        self.food_location = [(food.x, food.y)]


    def draw(self):
        WIN.fill(BLUE)
        for snake in self.snake_body:
            pygame.draw.rect(WIN, BLACK, [snake[0], snake[1], SNAKE_BLOCK, SNAKE_BLOCK])

    def update(self):
        self.x += self.x_change
        self.y += self.y_change

    def move(self, dirn):
        if dirn == KEY_LEFT:
            self.x_change = -SNAKE_BLOCK
            self.y_change= 0
        elif dirn == KEY_RIGHT:
            self.x_change = SNAKE_BLOCK
            self.y_change = 0
        elif dirn == KEY_UP:
            self.x_change = 0
            self.y_change = -SNAKE_BLOCK
        elif dirn == KEY_DOWN:
            self.x_change = 0
            self.y_change = SNAKE_BLOCK

    def is_dead(self):
        if self.x >= WIN_WIDTH or self.x < 0 or self.y >= WIN_HEIGHT or self.y < 0:
            return True
        return False

    def self_collide(self):
        snake_head = []
        snake_head.append(self.x)
        snake_head.append(self.y)
        self.snake_body.append(snake_head)
        if len(self.snake_body) > self.snake_length:
            del self.snake_body[0]

        for x in self.snake_body[:-1]:
            if x == snake_head:
                return True
        return False

    def body_collide(self, x, y):
        for snake in self.snake_body[:-1]:
            if x == snake[0] and y == snake[1]:
                return True
        return False

    def food_collide(self, x, y):
       if x == self.food.x and y == self.food.y:
           return True
       return False


    def wall_collide(slef, x, y):
        if x >= WIN_WIDTH or x < 0 or y >= WIN_HEIGHT or y < 0:
            return True
        return False

    def look(self):
        vision = []
        temp = self.look_in_direction(-SNAKE_BLOCK, 0)
        for t in temp:
            vision.append(t)
        temp = self.look_in_direction(-SNAKE_BLOCK, -SNAKE_BLOCK)
        for t in temp:
            vision.append(t)
        temp = self.look_in_direction(0, -SNAKE_BLOCK)
        for t in temp:
            vision.append(t)
        temp = self.look_in_direction(SNAKE_BLOCK, -SNAKE_BLOCK)
        for t in temp:
            vision.append(t)
        temp = self.look_in_direction(SNAKE_BLOCK, 0)
        for t in temp:
            vision.append(t)
        temp = self.look_in_direction(SNAKE_BLOCK, SNAKE_BLOCK)
        for t in temp:
            vision.append(t)
        temp = self.look_in_direction(0, SNAKE_BLOCK)
        for t in temp:
            vision.append(t)
        temp = self.look_in_direction(-SNAKE_BLOCK, SNAKE_BLOCK)
        for t in temp:
            vision.append(t)
        return vision

    def look_in_direction(self, x, y):
        look = [0]*3
        pos = [self.x, self.y]
        distance = 0
        food_found = False
        body_found = False
        pos[0] += x
        pos[1] += y
        distance += 1

        while not self.wall_collide(pos[0], pos[1]):
            if not food_found and self.food_collide(pos[0], pos[1]):
                food_found = True
                look[0] = 1
            if not body_found and self.body_collide(pos[0], pos[1]):
                body_found = True
                look[1] = 1
            pos[0] += x
            pos[1] += y
            distance += 1
        look[2] = 1/distance
        return look

    def draw_food_line(self, vision):
    	for i in range(0, 24, 3):
    		if vision[i] == 1:
    			pygame.draw.line(WIN, (255, 0, 0), (self.x+SNAKE_BLOCK/2, self.y+SNAKE_BLOCK/2), (self.food.x+SNAKE_BLOCK/2, self.food.y+SNAKE_BLOCK/2), 5)



class Food:
    def __init__(self):
        self.x = round(random.randrange(0, WIN_WIDTH - SNAKE_BLOCK) / SNAKE_BLOCK) * SNAKE_BLOCK
        self.y = round(random.randrange(0, WIN_HEIGHT - SNAKE_BLOCK) / SNAKE_BLOCK) * SNAKE_BLOCK

    def draw(self):
        pygame.draw.rect(WIN, GREEN, [self.x, self.y, SNAKE_BLOCK, SNAKE_BLOCK])

    def eaten_by(self, snake):
        if self.x == snake.x and self.y == snake.y:
            return True
        return False

def your_score(score):
    value = SCORE_FONT.render("Your Score: " + str(score), True, YELLOW)
    WIN.blit(value, [WIN_WIDTH - 10 - value.get_width(), 10])

def show_data(score, alive, gen):
    value = SCORE_FONT.render("Your Score: " + str(score), True, YELLOW)
    WIN.blit(value, [0, 0])
    value = SCORE_FONT.render("Alive: " + str(alive), True, YELLOW)
    WIN.blit(value, [0, 20])
    value = SCORE_FONT.render("Gen: " + str(gen), True, YELLOW)
    WIN.blit(value, [0, 40])

def main(genomes, config):
    global GEN, random_snake
    snake_score = []

    nets = []
    ge = []
    snakes = []
    foods = []
    GEN += 1

    game_over = False
    score = 0

    clock = pygame.time.Clock()
    

    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        food = Food()
        foods.append(food)
        snake = Snake(food)
        snakes.append(snake)
        g.fitness = 0
        ge.append(g)
        snake_score.append(snake)

    random_snake = random.choice(snakes)

    while not game_over:
        clock.tick(SNAKE_SPEED)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
                pygame.quit()
                quit()

        for x, snake in enumerate(snakes):
            dist = ((snake.x-foods[x].x)**2 + (snake.y-foods[x].y)**2)**0.5
            if snake.old_dist < dist:
            	ge[x].fitness += 0.1
            else:
            	ge[x].fitness -= 0.2
            snake.old_dist = dist
            out = nets[x].activate(snake.look())
            ind = out.index(max(out))
            snake.direction_gone.append(out)
            if ind == KEY_LEFT:
                snake.move(KEY_LEFT)
            elif ind == KEY_RIGHT:
                snake.move(KEY_RIGHT)
            elif ind == KEY_UP:
                snake.move(KEY_UP)
            elif ind == KEY_DOWN:
                snake.move(KEY_DOWN)

            snake.life_left -= 1
            if snake.life_left <= 0:
                ge[x].fitness -= 1
                snakes.pop(x)
                nets.pop(x)
                ge.pop(x)
                foods.pop(x)
                snake.dead = True


            if snake.is_dead():
                if len(snakes) >= x:
                    ge[x].fitness -= 1
                    snakes.pop(x)
                    nets.pop(x)
                    ge.pop(x)
                    foods.pop(x)
                    snake.dead = True

            if snake.self_collide():
                ge[x].fitness -= 1
                snakes.pop(x)
                nets.pop(x)
                ge.pop(x)
                foods.pop(x)
                snake.dead  =True

            snake.draw()
            snake.food.draw()
            snake.update()


            if snake.food.eaten_by(snake):
                foods[x].x = round(random.randrange(0, WIN_WIDTH - SNAKE_BLOCK) / SNAKE_BLOCK) * SNAKE_BLOCK
                foods[x].y = round(random.randrange(0, WIN_HEIGHT - SNAKE_BLOCK) / SNAKE_BLOCK) * SNAKE_BLOCK
                snake.food_location.append((foods[x].x, foods[x].y))
                snake.snake_length += 1
                ge[x].fitness += 10
                score += 1
                snake.foods_eaten += 1
                if snake.life_left < 500:
                	if snake.life_left > 400:
                		snake.life_left = 500
                	else:
                		snake.life_left += 100
        show_data(score, len(snakes), GEN)
        if DRAW_LINES:
        	snake.draw_food_line(snake.look())
        pygame.display.update()

        if len(snakes) <= 0:
            game_over = True
            break

    mfx = [x.foods_eaten for x in snake_score]
    mx = max(mfx)
    print("Max food eaten by snake #{} is {}".format(mfx.index(mx), mx))

def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)

    p = neat.Population(config)

    p.add_reporter(neat.StdOutReporter(True))
    stat = neat.StatisticsReporter()
    p.add_reporter(stat)

    winner = p.run(main, 100)

    print("\nBest genome:\n{!s}".format(winner))


if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-feedforward.txt")
    run(config_path)    