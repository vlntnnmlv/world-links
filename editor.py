from scipy.spatial import KDTree
from graphrenderer import GraphRenderer
from railwaynet import RailwayNetManager, COLORS
from guirenderer import GUIRenderer

import pygame as pg

class Editor:
    def __init__(self, railway_net_manager: RailwayNetManager):

        pg.init()
        
        # init application screen
        self.size = self.w, self.h = (1900, 900)
        self.screen = pg.display.set_mode(self.size)

        # set utility attributes
        self.running = False
        self.current_country = "full"

        # set graph data
        self.railway_net_manager = railway_net_manager

        # set renderers
        self.gui_surface = pg.Surface((1900, 50))
        self.graph_surface = pg.Surface((1900, 850))
        self.gui_renderer = GUIRenderer(self.gui_surface, self.railway_net_manager.countries_sorted)
        self.graph_renderer = GraphRenderer(self.graph_surface, self.railway_net_manager.full_graph, COLORS)

    def run(self):

        self.graph_renderer.render()
        
        self.running = True
        while self.running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        self.running = False

                result = self.gui_renderer.check_event(event)
                if result is not None:
                    if result == "full":
                        self.graph_renderer.update_graph(self.railway_net_manager.full_graph.get_biggest_component())
                    else:
                        self.graph_renderer.update_graph(self.railway_net_manager.get_net(result))
                    self.graph_renderer.render()
                
                result = self.graph_renderer.check_event(event)
                if result is not None:
                    self.railway_net_manager.save_node(result)
                    self.graph_renderer.render()

            self.gui_renderer.render()

            self.screen.blit(self.gui_surface, (0,0))
            self.screen.blit(self.graph_surface, (0,50))

            pg.display.update()
