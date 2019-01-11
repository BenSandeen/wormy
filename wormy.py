# Wormy (a Nibbles clone)
# By Al Sweigart al@inventwithpython.com
# http://inventwithpython.com/pygame
# Released under a "Simplified BSD" license

import random, pygame, sys
from typing import List
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
    # Set a random start point
    worm_1_controls = key_directions(K_LEFT, K_RIGHT, K_UP, K_DOWN)
    worm_2_controls = key_directions(K_a, K_d, K_w, K_s)
    worms = [Worm(GREEN, DARKGREEN, 1, worm_1_controls), Worm(ORANGE, DARKORANGE, 2, worm_2_controls)]
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
                elif event.key == K_ESCAPE:
                    terminate()

        # check if the worm has hit itself or the edge
        if worms[0].collided(worms[1]) or worms[1].collided(worms[0]):
            return  # game over
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

        for worm in worms:
            worm.draw_worm()
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


class Worm:
    def __init__(self, worm_body_color, worm_outline_color, worm_scoreboard_pos, control_keys: List):
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

    def draw_worm(self):
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


if __name__ == '__main__':
    main()
