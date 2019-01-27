# Wormy (a Nibbles clone)
# By Al Sweigart al@inventwithpython.com
# http://inventwithpython.com/pygame
# Released under a "Simplified BSD" license

import random, pygame, sys
from itertools import combinations
from copy import deepcopy
from collections import namedtuple
from pygame.locals import *

FPS = 15
WINDOWWIDTH  = 640 + 320
WINDOWHEIGHT = 480 + 240
CELLSIZE = 20
assert WINDOWWIDTH % CELLSIZE == 0, "Window width must be a multiple of cell size."
assert WINDOWHEIGHT % CELLSIZE == 0, "Window height must be a multiple of cell size."
CELLWIDTH = int(WINDOWWIDTH / CELLSIZE)
CELLHEIGHT = int(WINDOWHEIGHT / CELLSIZE)
MAXNUMAPPLES = 4

#                   R    G    B
WHITE           = (255, 255, 255)
BLACK           = (  0,   0,   0)
RED             = (255,   0,   0)
ORANGE          = (255, 131,  24)
DARKORANGE      = (181,  94,  17)
GREEN           = (  0, 255,   0)
DARKGREEN       = (  0, 155,   0)
DARKGRAY        = ( 40,  40,  40)
GRAY            = (120, 120, 120)
NU_PURPLE       = ( 91,  59, 140)
LIGHT_NU_PURPLE = (204, 196, 223)
BGCOLOR = BLACK

UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'

# For easy accessing of directions.  This lets us do things like:
# `if key_press == worm.key_directions.left:` rather than using the magic string "left"
key_directions = namedtuple("key_directions", ["left", "right", "up", "down"])

HEAD = 0  # syntactic sugar: index of the worm's head

def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT

    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    BASICFONT = pygame.font.Font('freesansbold.ttf', 18)
    pygame.display.set_caption('ALASKAN BULL WORMS!!!!!')

    showStartScreen()
    while True:
        runGame()
        showGameOverScreen()


def runGame():
    bullets = []
    stones = []
    # Set a random start point
    worm_1_controls = key_directions(K_LEFT, K_RIGHT, K_UP, K_DOWN)
    worm_2_controls = key_directions(K_a, K_d, K_w, K_s)
    worms = [Worm(GREEN, DARKGREEN, 1, worm_1_controls, K_RSHIFT),
             Worm(ORANGE, DARKORANGE, 2, worm_2_controls, K_e)]
    num_apples = 0

    # Start each of the apples in a random place
    apples = []
    while num_apples < MAXNUMAPPLES:
        new_apple = getRandomLocation()
        if new_apple in apples:
            continue
        else:
            apples.append(new_apple)
            num_apples += 1

    while True:  # main game loop
        for event in pygame.event.get():  # event handling loop
            if event.type == QUIT:
                terminate()
            elif event.type == KEYDOWN:
                if event.key in worms[0].control_keys:
                    worms[0].turn(event.key)
                elif event.key in worms[1].control_keys:
                    worms[1].turn(event.key)
                elif event.key == worms[0].shoot_key:
                    bullets.append(worms[0].shoot())
                elif event.key == worms[1].shoot_key:
                    bullets.append(worms[1].shoot())
                elif event.key == K_ESCAPE:
                    terminate()

        # `itertools.combinations(worms, 2)` gives all pairwise combinations of worms, so that if we have more than two
        # worms, we can still check for collisions between all of them
        for worm_a, worm_b in combinations(worms, 2):
            # check if the worm has hit itself, the other worm, or the edge
            if worm_a.collided(worm_b) or worm_b.collided(worm_a):
                return  # game over

        for worm in worms:
            if worm.hit_stone(stones):
                return  # game over

        bullets_hit = []
        for bullet in bullets:
            for worm in worms:
                shot_location = bullet.hit_worm(worm)
                if shot_location:
                    if shot_location == worm.get_head_pos():
                        return  # Headshot means game over!
                    stones += worm.lose_body(shot_location)
                    bullets_hit.append(bullet)

        # Remove the bullets that landed a shot and then have four new bullets explode from the location of the hit
        for bullet in bullets_hit:
            bullets.remove(bullet)
            bullets += bullet.explode()

        for worm in worms:
            for wormBody in worm.body[1:]:
                if wormBody['x'] == worm.body[HEAD]['x'] and wormBody['y'] == worm.body[HEAD]['y']:
                    return  # game over

            # check if worm has eaten an apple
            apple_was_eaten = False
            for apple in apples:
                if worm.body[HEAD]['x'] == apple['x'] and worm.body[HEAD]['y'] == apple['y']:
                    apples.remove(apple)
                    apples.append(getRandomLocation())  # set a new apple somewhere
                    apple_was_eaten = True

            if not apple_was_eaten:
                del worm.body[-1]  # remove worm's tail segment

            worm.move()

        DISPLAYSURF.fill(BGCOLOR)
        drawGrid()

        bullets_left_map = []
        for bullet in bullets:
            bullet.move()
            if bullet.left_map():
                bullets_left_map.append(bullet)

        for bullet in bullets_left_map:
            bullets.remove(bullet)

        for bullet in bullets:
            bullet.draw()

        for stone in stones:
            stone.draw()

        for worm in worms:
            worm.draw()
            worm.draw_score()

        drawApples(apples)
        pygame.display.update()
        FPSCLOCK.tick(FPS)


def drawPressKeyMsg():
    pressKeySurf = BASICFONT.render('Press a key to play.', True, DARKGRAY)
    pressKeyRect = pressKeySurf.get_rect()
    pressKeyRect.topleft = (WINDOWWIDTH - 200, WINDOWHEIGHT - 30)
    DISPLAYSURF.blit(pressKeySurf, pressKeyRect)


def checkForKeyPress():
    if len(pygame.event.get(QUIT)) > 0:
        terminate()

    keyUpEvents = pygame.event.get(KEYUP)
    if len(keyUpEvents) == 0:
        return None
    if keyUpEvents[0].key == K_ESCAPE:
        terminate()
    return keyUpEvents[0].key


def showStartScreen():
    # titleFont = pygame.font.Font('freesansbold.ttf', 67)
    titleFont = pygame.font.Font('C:\Windows\Fonts\HARRP__.ttf', 67)
    titleSurf1 = titleFont.render('ALASKAN BULL WORMS!', True, WHITE, NU_PURPLE)
    titleSurf2 = titleFont.render('ALASKAN BULL WORMS!', True, LIGHT_NU_PURPLE)

    degrees1 = 0
    degrees2 = 0
    while True:
        DISPLAYSURF.fill(BGCOLOR)
        rotatedSurf1 = pygame.transform.rotate(titleSurf1, degrees1)
        rotatedRect1 = rotatedSurf1.get_rect()
        rotatedRect1.center = (WINDOWWIDTH / 2, WINDOWHEIGHT / 2)
        DISPLAYSURF.blit(rotatedSurf1, rotatedRect1)

        rotatedSurf2 = pygame.transform.rotate(titleSurf2, degrees2)
        rotatedRect2 = rotatedSurf2.get_rect()
        rotatedRect2.center = (WINDOWWIDTH / 2, WINDOWHEIGHT / 2)
        DISPLAYSURF.blit(rotatedSurf2, rotatedRect2)

        drawPressKeyMsg()

        if checkForKeyPress():
            pygame.event.get()  # clear event queue
            return
        pygame.display.update()
        FPSCLOCK.tick(FPS)
        degrees1 += 3  # rotate by 3 degrees each frame
        degrees2 += 7  # rotate by 7 degrees each frame


def terminate():
    pygame.quit()
    sys.exit()


def getRandomLocation():
    return {'x': random.randint(0, CELLWIDTH - 1), 'y': random.randint(0, CELLHEIGHT - 1)}


def showGameOverScreen():
    gameOverFont = pygame.font.Font('freesansbold.ttf', 150)
    gameSurf = gameOverFont.render('Game', True, WHITE)
    overSurf = gameOverFont.render('Over', True, WHITE)
    gameRect = gameSurf.get_rect()
    overRect = overSurf.get_rect()
    gameRect.midtop = (WINDOWWIDTH / 2, 10)
    overRect.midtop = (WINDOWWIDTH / 2, gameRect.height + 10 + 25)

    DISPLAYSURF.blit(gameSurf, gameRect)
    DISPLAYSURF.blit(overSurf, overRect)
    drawPressKeyMsg()
    pygame.display.update()
    pygame.time.wait(500)
    checkForKeyPress()  # clear out any key presses in the event queue

    while True:
        if checkForKeyPress():
            pygame.event.get()  # clear event queue
            return


def drawApples(coords):
    for coord in coords:
        x = coord['x'] * CELLSIZE
        y = coord['y'] * CELLSIZE
        appleRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
        pygame.draw.rect(DISPLAYSURF, RED, appleRect)


def drawGrid():
    for x in range(0, WINDOWWIDTH, CELLSIZE):  # draw vertical lines
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (x, 0), (x, WINDOWHEIGHT))
    for y in range(0, WINDOWHEIGHT, CELLSIZE):  # draw horizontal lines
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (0, y), (WINDOWWIDTH, y))


class Bullet:
    def __init__(self, position, direction):
        self.position = position
        self.direction = direction

    def move(self):
        """Bullets move twice as fast as the worms"""
        if self.direction == UP:
            self.position['y'] -= 2
        elif self.direction == DOWN:
            self.position['y'] += 2
        elif self.direction == LEFT:
            self.position['x'] -= 2
        elif self.direction == RIGHT:
            self.position['x'] += 2

    def hit_worm(self, worm):
        """Checks whether it has hit the given worm

        :returns: The position where the worm was hit
        """
        for body_segment in worm.body:
            if self.position == body_segment:
                return self.position  # worm has been hit
        return None

    def explode(self):
        """When bullets land a hit on a worm, they explode, sending out two new bullets, one forward (in the same
        direction as the bullet) and one backward

        :return: 2 new bullets
        """
        opposite_direction = None
        if self.direction == UP:
            opposite_direction = DOWN
        elif self.direction == DOWN:
            opposite_direction = UP
        elif self.direction == LEFT:
            opposite_direction = RIGHT
        elif self.direction == RIGHT:
            opposite_direction = LEFT

        # We need to deep copy these otherwise they'll both be referring to the same underlying positions
        return [Bullet(deepcopy(self.position), deepcopy(self.direction)),
                Bullet(deepcopy(self.position), deepcopy(opposite_direction))]

    def left_map(self):
        """Checks whether the bullet has run off the edge of the map

        :return: True if the bullet is off the map, False otherwise
        """
        if self.position['x'] <= -1 or self.position['x'] >= CELLWIDTH or \
                self.position['y'] <= -1 or self.position['y'] >= CELLHEIGHT:
            return True
        return False

    def draw(self):
        x = self.position['x'] * CELLSIZE
        y = self.position['y'] * CELLSIZE
        bullet_rect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
        pygame.draw.rect(DISPLAYSURF, NU_PURPLE, bullet_rect)
        bullet_inner_rect = pygame.Rect(x + 4, y + 4, CELLSIZE - 8, CELLSIZE - 8)
        pygame.draw.rect(DISPLAYSURF, LIGHT_NU_PURPLE, bullet_inner_rect)


class Stone:
    def __init__(self, stone_position):
        self.stone_position = stone_position

    def draw(self):
        # for coord in self.stone_position:
        x = self.stone_position['x'] * CELLSIZE
        y = self.stone_position['y'] * CELLSIZE
        stone_rect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
        pygame.draw.rect(DISPLAYSURF, DARKGRAY, stone_rect)
        stone_inner_rect = pygame.Rect(x + 4, y + 4, CELLSIZE - 8, CELLSIZE - 8)
        pygame.draw.rect(DISPLAYSURF, GRAY, stone_inner_rect)

    def get_position(self):
        return self.stone_position

class Worm:
    def __init__(self, worm_body_color, worm_outline_color, worm_scoreboard_pos, control_keys, shoot_key):
        startx = random.randint(5, CELLWIDTH - 6)
        starty = random.randint(5, CELLHEIGHT - 6)
        self.body = [{'x': startx,     'y': starty},
                     {'x': startx - 1, 'y': starty},
                     {'x': startx - 2, 'y': starty}]
        self.direction = RIGHT

        self.body_color = worm_body_color
        self.outline_color = worm_outline_color
        self.scoreboard_pos = worm_scoreboard_pos
        self.control_keys = control_keys
        self.shoot_key = shoot_key

    def collided(self, other_worm):
        # See if worm collided with itself or the edge of the map
        if self.body[HEAD]['x'] == -1 or self.body[HEAD]['x'] == CELLWIDTH or \
                self.body[HEAD]['y'] == -1 or self.body[HEAD]['y'] == CELLHEIGHT:
            return True  # game over

        # See if worm collided with other worm
        for body_segment in self.body:
            if body_segment in [segment_coords for segment_coords in other_worm.body]:
                return True  # game over

    def turn(self, key):
        if key == self.control_keys.left and self.direction != RIGHT:
            self.direction = LEFT
        elif key == self.control_keys.right and self.direction != LEFT:
            self.direction = RIGHT
        elif key == self.control_keys.up and self.direction != DOWN:
            self.direction = UP
        elif key == self.control_keys.down and self.direction != UP:
            self.direction = DOWN

    def move(self):
        if self.direction == UP:
            newHead = {'x': self.body[HEAD]['x'], 'y': self.body[HEAD]['y'] - 1}
        elif self.direction == DOWN:
            newHead = {'x': self.body[HEAD]['x'], 'y': self.body[HEAD]['y'] + 1}
        elif self.direction == LEFT:
            newHead = {'x': self.body[HEAD]['x'] - 1, 'y': self.body[HEAD]['y']}
        elif self.direction == RIGHT:
            newHead = {'x': self.body[HEAD]['x'] + 1, 'y': self.body[HEAD]['y']}

        self.body.insert(0, newHead)

    def draw(self):
        for coord in self.body:
            x = coord['x'] * CELLSIZE
            y = coord['y'] * CELLSIZE
            wormSegmentRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
            pygame.draw.rect(DISPLAYSURF, self.outline_color, wormSegmentRect)
            wormInnerSegmentRect = pygame.Rect(x + 4, y + 4, CELLSIZE - 8, CELLSIZE - 8)
            pygame.draw.rect(DISPLAYSURF, self.body_color, wormInnerSegmentRect)

    def draw_score(self):
        scoreSurf = BASICFONT.render('Score: %s' % (len(self.body)), True, WHITE)
        scoreRect = scoreSurf.get_rect()
        scoreRect.topleft = (WINDOWWIDTH - self.scoreboard_pos * 120, 10)
        DISPLAYSURF.blit(scoreSurf, scoreRect)

    def lose_body(self, position):
        """If the worm is hit by a bullet, the posterior portion of its body, beginning with where the worm was hit,
        is lost, and it falls off and becomes an obstacle
        """
        segments_to_lose = []
        remaining_segments_lost = False
        for body_segment in self.body:
            if remaining_segments_lost:
                segments_to_lose.append(body_segment)
            elif body_segment == position:
                remaining_segments_lost = True

        # We still need to actually cut off the remaining segments
        [self.body.remove(body_segment) for body_segment in segments_to_lose]
        return [Stone(segment) for segment in segments_to_lose]

    def shoot(self):
        if self.direction == UP:
            bullet_initial_position = {'x': self.body[HEAD]['x'], 'y': self.body[HEAD]['y'] - 1}
        elif self.direction == DOWN:
            bullet_initial_position = {'x': self.body[HEAD]['x'], 'y': self.body[HEAD]['y'] + 1}
        elif self.direction == LEFT:
            bullet_initial_position = {'x': self.body[HEAD]['x'] - 1, 'y': self.body[HEAD]['y']}
        elif self.direction == RIGHT:
            bullet_initial_position = {'x': self.body[HEAD]['x'] + 1, 'y': self.body[HEAD]['y']}

        return Bullet(bullet_initial_position, self.direction)

    def hit_stone(self, stones):
        stone_positions = [stone.get_position() for stone in stones]
        for body_segment in self.body:
            if body_segment in stone_positions:
                return True

    def get_head_pos(self):
        return self.body[HEAD]


if __name__ == '__main__':
    main()
