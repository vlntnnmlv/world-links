import pygame as pg
import pandas as pd

class Editor:
    def __init__(self, graph_data):
        pg.init()
        self.size = self.w, self.h = (1080, 720)
        self.screen = pg.display.set_mode(self.size)
        self.running = False
        self.graph_data = graph_data
        self.vertical_bounds = self.graph_data.lat.min(), self.graph_data.lat.max()
        self.horizontal_bounds = self.graph_data.lon.min(), self.graph_data.lon.max()
        self.vertical_span = self.vertical_bounds[1] - self.vertical_bounds[0]
        self.horizontal_span = self.horizontal_bounds[1] - self.horizontal_bounds[0]

    def run(self):
        self.running = True
        while self.running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        self.running = False

            self.screen.fill((190,190,160))
            pg.display.flip()

if __name__ == "__main__":
    pass