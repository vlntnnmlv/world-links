from scipy.spatial import KDTree
from graphrenderer import GraphRenderer
from railwaynet import RailwayNetManager, COLORS
from guirenderer import GUIRenderer
from threading import Thread
import pygame as pg

class Editor:
    def __init__(self, railway_net_manager: RailwayNetManager):

        pg.init()
        
        # init application screen
        self.size = self.w, self.h = (1900, 900)
        self.screen = pg.display.set_mode(self.size)
        self.screen.fill((255, 240, 250))
        pg.display.flip()

        # set utility attributes
        self.running = False
        self.current_country = "full"
        self.search_range = 2
        self.current_paths = [None, None]

        # set graph data
        self.railway_net_manager = railway_net_manager

        # set renderers
        self.gui_surface = pg.Surface((1900, 50))
        self.graph_surface = pg.Surface((1900, 850))
        self.gui_renderer = GUIRenderer(self.gui_surface, self.railway_net_manager.countries_sorted)
        self.graph_renderer = GraphRenderer(
            self.graph_surface,
            self.railway_net_manager.full_graph.get_biggest_component(),
            COLORS,
            self.search_range
            )

    def find_path_routine(self):
        self.railway_net_manager.find_path(self.current_paths)
        self.graph_renderer.render()
        animate = False
        if self.current_paths[1] is not None:
            if self.current_paths[0] is not None:
                self.current_country = "full"
                self.graph_renderer.update_graph(self.railway_net_manager.full_graph.get_biggest_component())
                self.graph_renderer.render(animate=True)

            self.graph_renderer.update_path(self.current_paths[1])
            self.graph_renderer.render()

    def manage_guirenderer_event(self, event: pg.event):
        result = self.gui_renderer.check_event(event)
        if result is not None:
            if result == "reset":
                self.railway_net_manager.start_node = None
                self.railway_net_manager.finish_node = None
                self.graph_renderer.path = None
                self.graph_renderer.path_points_data = None
            else:            
                self.current_country = result
                if result == "full":
                    self.graph_renderer.update_graph(self.railway_net_manager.full_graph.get_biggest_component())
                else:
                    self.graph_renderer.update_graph(self.railway_net_manager.get_net(result))
            self.graph_renderer.render()

    def manage_graphrenderer_event(self, event: pg.event):
        result = self.graph_renderer.check_event(event)
        if result is not None:
            self.railway_net_manager.save_node(result, self.current_country)
            self.graph_renderer.render()
            if self.railway_net_manager.start_node is not None and \
                self.railway_net_manager.finish_node is not None:
                t = Thread(target=self.find_path_routine)
                t.start()


    def run(self):
        self.graph_renderer.render(animate=True)
        self.path = None

        self.running = True
        while self.running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        self.running = False

                self.manage_guirenderer_event(event)

                if self.current_country != "full":
                    self.manage_graphrenderer_event(event)


            self.gui_renderer.render()

            self.screen.blit(self.gui_surface, (0,0))
            self.screen.blit(self.graph_surface, (0,50))

            pg.draw.circle(self.screen, 'blue', pg.mouse.get_pos(), self.search_range, 1)

            pg.display.update()
