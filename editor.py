from importlib.util import module_for_loader
import pygame as pg
import pygame_gui as pgg
import pandas as pd
import numpy as np

class Editor:
    def __init__(self, graph_data):
        print(graph_data.shape)
        pg.init()
        self.size = self.w, self.h = (1080, 720, )
        self.screen = pg.display.set_mode(self.size)
        self.running = False
        self.graph_data = graph_data
        self.vertical_bounds = self.graph_data.lat.min(), self.graph_data.lat.max()
        self.horizontal_bounds = self.graph_data.lon.min(), self.graph_data.lon.max()
        self.vertical_span = self.vertical_bounds[1] - self.vertical_bounds[0]
        self.horizontal_span = self.horizontal_bounds[1] - self.horizontal_bounds[0]
        
        self.manager = pgg.UIManager(self.size)
        self.clock = pg.time.Clock()

        self.point_label = None

    def draw_points(self):
        self.screen.fill((190,190,160))
        screen_lat = []
        screen_lon = []
        for i in self.graph_data.index:
            coord = (
                (self.graph_data.lon.iloc[i] - self.horizontal_bounds[0]) / self.horizontal_span * self.w,
                (self.graph_data.lat.iloc[i] - self.vertical_bounds[0]) / self.vertical_span * self.h
                )
            screen_lat.append(coord[1])
            screen_lon.append(coord[0])

            pg.draw.circle(self.screen, 'red', coord, 1)
        self.graph_data['lat_screen'] = screen_lat
        self.graph_data['lon_screen'] = screen_lon

    def redraw_points(self):

        self.screen.fill((190,190,160))
        for i in self.graph_data.index:
            coord = (
                self.graph_data.lon_screen.iloc[i],
                self.graph_data.lat_screen.iloc[i]
                )
            pg.draw.circle(self.screen, 'red', coord, 1)

    def run(self):
        
        self.draw_points()
   
        self.running = True
        while self.running:
            time_delta = self.clock.tick(60)/1000.0
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        self.running = False

            for i in self.graph_data.index:
                screen_coord = (
                    self.graph_data.lon_screen.iloc[i],
                    self.graph_data.lat_screen.iloc[i]
                    )
                mouse_coord = pg.mouse.get_pos()
                if abs(mouse_coord[0] - screen_coord[0]) < 2 and \
                    abs(mouse_coord[1] - screen_coord[1]) < 2:
                    if self.point_label is not None and screen_coord != self.labeled_point:
                        self.point_label.remove(self.point_label.ui_group)
                        self.redraw_points()
                    self.labeled_point = screen_coord
                    self.point_label = pgg.elements.UILabel(relative_rect=pg.Rect(pg.mouse.get_pos(), (100, 50)),
                                        text='Say Hello',
                                        manager=self.manager)


                self.manager.process_events(event)
            self.manager.update(time_delta)
            self.manager.draw_ui(self.screen)
            pg.display.flip()

            
if __name__ == "__main__":
    graph_data = pd.DataFrame(np.random.rand(500, 2), columns=['lat', 'lon'])
    editor = Editor(graph_data)
    editor.run()