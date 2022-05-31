from railwaynet import *
from scipy.spatial import cKDTree
import pygame as pg


class GraphRenderer:
    
    # region Construction
    
    def __init__(self, surface: pg.Surface, graph: RailwayNet, colors: list[str], bg_color: tuple[int, int, int] = (0,0,0)):
        self.surface = surface
        self.size = self.w, self.h = self.surface.get_size()
        
        self.bg_color = bg_color
        self.colors = colors
        
        self.graph = graph
        self.points_data = None
        self.search_tree = None
        
        self.update_points_positions()
        self.update_search_tree()

    # endregion

    # region PublicMethods

    def update_points_positions(self) -> None:
        self.points_data = self.graph.get_points_dataframe()
        
        vertical_bounds = self.points_data.lat.max(), self.points_data.lat.min()
        horizontal_bounds = self.points_data.lon.min(), self.points_data.lon.max()
        vertical_span = vertical_bounds[1] - vertical_bounds[0]
        horizontal_span = horizontal_bounds[1] - horizontal_bounds[0]

        self.points_data['x'] = self.points_data.lon.apply(
                lambda lon : (lon - horizontal_bounds[0]) / horizontal_span * self.w
            )
        self.points_data['y'] = self.points_data.lat.apply(
                lambda lat : (lat - vertical_bounds[0]) / vertical_span * self.h
            )
        self.points_data['color'] = self.points_data.iso3.apply(
                lambda iso3: self.colors[ord(iso3[0]) % len(self.colors)]
            )
        self.points_data['radius'] = [1] * self.points_data.shape[0]

    def update_search_tree(self) -> None:
        self.search_tree = cKDTree(
            [(self.points_data.x.iloc[i], self.points_data.y.iloc[i]) for i in self.points_data.index]
        )

    def update_graph(self, graph: RailwayNet) -> None:
        self.graph = graph
        self.update_points_positions()
        self.update_search_tree()

    def check_event(self, event: pg.event) -> tuple[float, float] | None:
        if event.type == pg.MOUSEBUTTONDOWN:
            print("G2")
            mouse_coord = pg.mouse.get_pos()
            found_points = self.search_tree.query_ball_point(mouse_coord, r=2)
            if found_points:
                print("G3")
                point_index = found_points[0]
                self.points_data.color.iloc[point_index] = 'red'
                self.points_data.radius.iloc[point_index] = 4
                return (
                    self.points_data.lon.iloc[point_index],
                    self.points_data.lat.iloc[point_index]
                    )
            

    def render(self) -> None:
        self.surface.fill(self.bg_color)
        for i in self.points_data.index:
            pg.draw.circle(
                self.surface,
                self.points_data.color.iloc[i],
                (self.points_data.x.iloc[i], self.points_data.y.iloc[i]),
                self.points_data.radius.iloc[i]
                )

    # endregion
    