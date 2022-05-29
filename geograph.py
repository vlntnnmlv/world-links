import networkx as nx

from matplotlib import pyplot as plt
from geopy import distance

class Color:

    # region construction

    def __init__(self, r: float, g: float, b: float):
        self.r = r
        self.g = g
        self.b = b
        self.rgb = (self.r, self.g, self.b)

    # endregion

class Point:

    # region Construction

    def __init__(self, lat: float, lon: float):
        self.lat = lat
        self.lon = lon
        self.coord = (lon, lat)
        self.coord_reverse = (lat, lon)

    # endregion

    # region PublicMethods
    
    def distance(self, other) -> float:
        return distance.distance(self.coord_reverse, other.coord_reverse).km
    
    # endregion

    # region OverloadMethods

    def __eq__(self, other):
        return self.lat == other.lat and self.lon == other.lon

    def __hash__(self):
        return hash(self.coord)

    # endregion

class GeoGraph(nx.Graph):

    # region Construction

    def __init__(self):
        super(GeoGraph, self).__init__()

    # endregion

    # region PublicMethods

    def draw(self, edge_color=None, node_color=None, width=None, node_size=None):
        nx.draw(self,
                edgelist=self.edges,
                edge_color='black' if edge_color is None else edge_color,
                width=1 if width is None else width,
                nodelist=self.nodes,
                node_color='red' if node_color is None else node_color,
                node_size=1 if node_size is None else node_size,
                pos=dict(zip(self.nodes, [node.coord for node in self.nodes]))
                )

    # endregion