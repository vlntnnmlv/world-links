import pygame
from numba import njit
from pandas import DataFrame
from math import sqrt
from numpy.random import uniform

class KeyHoldController:
    K_UP = False
    K_DOWN = False
    K_LEFT = False
    K_RIGHT = False
    K_EQUALS = False
    K_MINUS = False
    K_SHIFT = K_UP | K_DOWN | K_LEFT | K_RIGHT
    K_ZOOM = K_EQUALS | K_MINUS 

@njit
def _shift(r, span, offset):
    return r + offset

@njit
def _zoom(r, span, zoom):
    return (r - span / 2) * zoom + span / 2

class App:
    def __init__(self, data : DataFrame):
        pygame.init()
        self.size = self.width, self.height = 1080, 720
        self.running = False
        self.screen = pygame.display.set_mode(self.size)
        self.data = data
        self.clock = pygame.time.Clock()

        self.data['X'] = \
            self.data['Longitude'].apply(lambda lon : (lon + 180) / 360 * self.width)
        self.data['Y'] = \
            self.data['Latitude'].apply(lambda lat : 1.05 * self.height - (lat + 90) / 180 * self.height)

        self.data['Cur_X'] = self.data['X']
        self.data['Cur_Y'] = self.data['Y']

        self.x_offset = 0
        self.y_offset = 0
        self.zoom     = 1

    def do_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.running = False
            if event.key == pygame.K_LEFT:
                KeyHoldController.K_LEFT = True
            elif event.key == pygame.K_RIGHT:
                KeyHoldController.K_RIGHT = True
            elif event.key == pygame.K_DOWN:
                KeyHoldController.K_DOWN = True
            elif event.key == pygame.K_UP:
                KeyHoldController.K_UP = True
            elif event.key == pygame.K_EQUALS:
                KeyHoldController.K_EQUALS = True
            elif event.key == pygame.K_MINUS:
                KeyHoldController.K_MINUS = True

            elif event.key == pygame.K_0:
                self.data.Cur_X = self.data.X
                self.data.Cur_Y = self.data.Y

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                KeyHoldController.K_LEFT = False
            elif event.key == pygame.K_RIGHT:
                KeyHoldController.K_RIGHT = False
            elif event.key == pygame.K_DOWN:
                KeyHoldController.K_DOWN = False
            elif event.key == pygame.K_UP:
                KeyHoldController.K_UP = False
            elif event.key == pygame.K_EQUALS:
                KeyHoldController.K_EQUALS = False
            elif event.key == pygame.K_MINUS:
                KeyHoldController.K_MINUS = False

    def run(self):
        self.running = True
        while self.running:
            for event in pygame.event.get():
                self.do_event(event)

            # do calculations
            if (KeyHoldController.K_LEFT):
                self.data.Cur_X = self.data.Cur_X.apply(lambda x : _shift(x, self.width, 2))
            if (KeyHoldController.K_RIGHT):
                self.data.Cur_X = self.data.Cur_X.apply(lambda x : _shift(x, self.width, -2))
            if (KeyHoldController.K_DOWN):
                self.data.Cur_Y = self.data.Cur_Y.apply(lambda y : _shift(y, self.height, -2))
            if (KeyHoldController.K_UP):
                self.data.Cur_Y = self.data.Cur_Y.apply(lambda y : _shift(y, self.height, 2))
            if (KeyHoldController.K_EQUALS):
                self.data.Cur_X = self.data.Cur_X.apply(lambda x : _zoom(x, self.width, 1.01))
                self.data.Cur_Y = self.data.Cur_Y.apply(lambda y : _zoom(y, self.height, 1.01))
                self.zoom *= 1.01
            if (KeyHoldController.K_MINUS):
                self.data.Cur_X = self.data.Cur_X.apply(lambda x : _zoom(x, self.width, 0.99))
                self.data.Cur_Y = self.data.Cur_Y.apply(lambda y : _zoom(y, self.height, 0.99))
                self.zoom *= 0.99

            # draw
            self.screen.fill((0,0,0))
            self.draw()
            pygame.display.flip()
        
        
        pygame.quit()        
    
    def draw(self):

        # draw airports
        for x, y in zip(self.data.Cur_X, self.data.Cur_Y):
            pygame.draw.circle(
                self.screen,
                (255,0,0),
                (x,y),
                1)
