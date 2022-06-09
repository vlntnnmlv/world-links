from railwaynet import *
from scipy.spatial import cKDTree
from threading import Thread

import pygame as pg


class GraphRenderer:
    
    # region Construction
    
    def __init__(
            self,
            surface: pg.Surface,
            fgraph: RailwayNet,
            graph: RailwayNet,
            colors: list[str],
            search_range: int = 2,
            bg_color: tuple[int, int, int] = (0,0,0)
        ):
        self.surface = surface
        self.size = self.w, self.h = self.surface.get_size()
        
        self.bg_color = bg_color
        self.colors = colors
        
        # full graph
        self.fgraph = fgraph
        self.fgraph_surface = None

        # displayed graph
        self.graph = graph
        self.points_data = None

        self.path = None
        self.path_points_data = None

        self.search_tree = None
        self.search_range = search_range

        self.update_points_positions()
        self.update_search_tree()

    # endregion

    # region PublicMethods

    def update_points_positions(self) -> None:
        self.points_data = self.graph.get_points_dataframe(self.fgraph)
        
        self.vertical_bounds = self.points_data.lat.max(), self.points_data.lat.min()
        self.horizontal_bounds = self.points_data.lon.min(), self.points_data.lon.max()
        self.vertical_span = self.vertical_bounds[1] - self.vertical_bounds[0]
        self.horizontal_span = self.horizontal_bounds[1] - self.horizontal_bounds[0]

        self.points_data['x'] = self.points_data.lon.apply(
                lambda lon : self.world2local(lon)
            )
        self.points_data['y'] = self.points_data.lat.apply(
                lambda lat : self.world2local(lat, horizontal=False)
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
        if self.path is not None:
            self.update_path_points_positions()

    def update_path_points_positions(self):
        if self.path_points_data is None:
            self.path_points_data = pd.DataFrame()
        self.path_points_data['x'] = [self.world2local(point.coord[0]) for point in self.path]
        self.path_points_data['y'] = [self.world2local(point.coord[1], horizontal=False) for point in self.path]

    def update_path(self, path: list[Point]):
        self.path = path
        self.update_path_points_positions()

    def check_event(self, event: pg.event) -> tuple[float, float] | None:
        if event.type == pg.MOUSEBUTTONDOWN:
            mouse_coord = pg.mouse.get_pos()
            mouse_coord = (mouse_coord[0], mouse_coord[1] - 50) 
            found_points = self.search_tree.query_ball_point(mouse_coord, r=self.search_range)
            if found_points:
                point_index = found_points[0]
                self.points_data.loc[:, ('color')].iloc[point_index] = 'red'
                self.points_data.loc[:, ('radius')].iloc[point_index] = 3
                return (
                    self.points_data.lon.iloc[point_index],
                    self.points_data.lat.iloc[point_index]
                    )
    
    def render(self, animate=False) -> None:
        if animate:
            t = Thread(target=self.render_internal)
            t.start()
        else:
            self.render_internal()

    def render_internal(self) -> None:
        if self.graph == self.fgraph and self.fgraph_surface is not None:
            self.surface.blit(self.fgraph_surface, (0,0))
        else:
            self.surface.fill(self.bg_color)
            for i in self.points_data.index:
                pg.draw.rect(
                    self.surface,
                    self.points_data.color.iloc[i],
                    pg.Rect(
                        (self.points_data.x.iloc[i], self.points_data.y.iloc[i]),
                        (self.points_data.radius.iloc[i], self.points_data.radius.iloc[i])),
                    self.points_data.radius.iloc[i]
                    )
        
        if self.graph == self.fgraph and self.fgraph_surface is None:
            self.fgraph_surface = pg.Surface(self.size)
            self.fgraph_surface.blit(self.surface, (0,0))

        if self.path_points_data is not None:
            for i in self.path_points_data.index[:-1]:
                pg.draw.line(
                    self.surface,
                    'red',
                    (self.path_points_data.x.iloc[i], self.path_points_data.y.iloc[i]),
                    (self.path_points_data.x.iloc[i + 1], self.path_points_data.y.iloc[i + 1]),
                    2
                )

    # endregion

    # region ServiceMethods

    def world2local(self, value: float, horizontal: bool = True):
        if horizontal:
            return (value - self.horizontal_bounds[0]) / self.horizontal_span * self.w
        return (value - self.vertical_bounds[0]) / self.vertical_span * self.h

    # endregion
