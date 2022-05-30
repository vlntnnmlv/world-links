from scipy.spatial import KDTree

import pygame as pg
import pygame_gui as pgg
import pandas as pd
import numpy as np
import networkx as nx

class Editor:
    def __init__(self, graph_data, graph):
        pg.init()

        self.size = self.w, self.h = (1800, 900, )
        self.screen = pg.display.set_mode(self.size)
        self.background_color = (250, 250, 245)
        self.running = False
        self.graph_data = graph_data
        self.graph = graph
        self.vertical_bounds = self.graph_data.lat.max(), self.graph_data.lat.min()
        self.horizontal_bounds = self.graph_data.lon.min(), self.graph_data.lon.max()
        self.vertical_span = self.vertical_bounds[1] - self.vertical_bounds[0]
        self.horizontal_span = self.horizontal_bounds[1] - self.horizontal_bounds[0]
        
        self.manager = pgg.UIManager(self.size, theme_path='theme.json')
        self.clock = pg.time.Clock()

        self.point_label = None
        self.labeled_point = None
        self.search_tree = None

        self.search_mode = False

        self.frm = None
        self.to  = None

    def draw_points(self):
        self.screen.fill(self.background_color)
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
        self.graph_data['radius']     = [1]*self.graph_data.shape[0]

        self.search_tree = KDTree(
                [   
                    (
                        self.graph_data.lon_screen.iloc[i],
                        self.graph_data.lat_screen.iloc[i]
                    )
                    for i in self.graph_data.index
                ],
                leafsize=20
            )

    def redraw_points(self):

        self.screen.fill(self.background_color)
        for i in self.graph_data.index:
            coord = (
                self.graph_data.lon_screen.iloc[i],
                self.graph_data.lat_screen.iloc[i]
                )
            pg.draw.circle(self.screen, 'red', coord, self.graph_data.radius.iloc)

    def find_point(self):
        mouse_coord = pg.mouse.get_pos()
        search_results = self.search_tree.query_ball_point(mouse_coord, r=2, workers=-1)
        if search_results:
            return search_results[0], (
                self.graph_data.lon.iloc[search_results[0]],
                self.graph_data.lat.iloc[search_results[0]]
                )
        return -1, None

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
                    if event.key == pg.K_s:
                        self.search_mode = not self.search_mode
                        if self.search_mode == False:
                            self.point_label.remove(self.point_label.groups)
                            self.redraw_points()

                if event.type == pg.MOUSEBUTTONDOWN:
                    i, point = self.find_point()
                    for node in self.graph.nodes:
                        if node.coord == point:
                            if self.frm is not None:
                                self.to = node
                                print("to set")

                                self.search_mode = False

                                path = nx.dijkstra_path(self.graph, self.frm, self.to, "distance")

                                def to_local(p):
                                    x = (p[0] - self.horizontal_bounds[0]) / self.horizontal_span * self.w
                                    y = (p[1] - self.vertical_bounds[0]) / self.vertical_span * self.h                       
                                    return (x,y)
                                
                                for i in range(len(path) - 1):
                                    pg.draw.line(
                                        self.screen,
                                        'black',
                                        to_local(path[i].coord),
                                        to_local(path[i + 1].coord),
                                        width=2
                                        )
                                pg.display.flip()


                            else:
                                self.frm = node
                                print("frm set")

                self.manager.process_events(event)

            if self.search_mode:
                index, nearest_point = self.find_point()
                if nearest_point is not None:
                    if self.labeled_point != nearest_point:
                        if self.labeled_point is not None:
                            self.redraw_points()
                            self.point_label.remove(self.point_label.ui_group)

                        self.labeled_point = nearest_point
                        self.point_label = pgg.elements.UILabel(
                            relative_rect=pg.Rect(pg.mouse.get_pos(), (100, 50)),
                            text=self.graph_data.iso3.iloc[index],
                            manager=self.manager)

            self.manager.update(time_delta)
            self.manager.draw_ui(self.screen)
            pg.display.flip()
            
if __name__ == "__main__":
    graph_data = pd.DataFrame(np.random.rand(500, 2), columns=['lat', 'lon'])
    graph_data['iso3'] = ['UKR' for _ in range(500)]
    editor = Editor(graph_data)
    editor.run()