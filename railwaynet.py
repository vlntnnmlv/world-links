from matplotlib import pyplot as plt
from tqdm import tqdm

import networkx as nx
import pandas as pd


class Point:

    # region Construction

    def __init__(self, lat: float, lon: float):
        self.lat = lat
        self.lon = lon
        self.coord = (lon, lat)
        self.coord_reverse = (lat, lon)

    def __eq__(self, other):
        return self.lat == other.lat and self.lon == other.lon

    def __hash__(self):
        return hash(self.coord)

    # endregion


class RailwayNetContainer(dict):

    # region Construction

    def __init__(self, data: pd.DataFrame):
        self.raw_data = data
        self.countries_sorted = data.iso3.value_counts().keys().to_list()
        super(RailwayNetContainer, self).__init__(zip(self.countries_sorted, (None for _ in self.countries_sorted)))

    # endregion

    # region PublicMethods

    def get_net(self, iso3: str):
        if iso3 in self.countries_sorted:
            if self[iso3] is None:
                self[iso3] = RailwayNet(self.raw_data, iso3)
            return self[iso3]
        return None

    # endregion


class RailwayNet(nx.Graph):

    # region Construction

    def __init__(self, data: pd.DataFrame = None, iso3: str = None):
        super(RailwayNet, self).__init__()
        if data is None:
            return

        country_condition = True if iso3 is None else data.iso3 == iso3
        for trail in data[country_condition]['shape']:
            lat, lon = RailwayNet.__get_coordinates_from_string(trail)
            self.add_node(Point(lon[0], lat[0]))
            for i in range(len(lat) - 1):
                b = Point(lon[i + 1], lat[i + 1])
                a = Point(lon[i], lat[i])
                self.add_node(b)
                if (a != b) and \
                        (a.lat != b.lat or a.lon != b.lon):
                    self.add_edge(a, b)
    # endregion

    # region PublicMethods

    def draw(self, size: tuple[int, int], show_components: bool = False):
        """ function which draws train railways graph """

        plt.figure(figsize=size)

        if not show_components:
            nx.draw(
                self,
                nodelist=self.nodes,
                node_size=[0 for v in self.nodes],
                pos=dict(zip(self.nodes, (node.coord for node in self.nodes)))
            )
        else:
            components = sorted(nx.connected_components(self), key=len, reverse=True)[:20]
            components_number = nx.number_connected_components(self)
            if components_number > 20:
                components_number = 20

            for index, component in enumerate(tqdm(components)):
                nx.draw(
                    self.subgraph(component),
                    nodelist=self.nodes,
                    node_size=[0 for v in self.nodes],
                    pos=dict(zip(self.nodes, (node.coord for node in self.nodes))),
                    edge_color=(index / components_number, index / 2 / components_number, index / 3 / components_number, )
                )
        plt.show()

    def __str__(self):
        res = ""
        res += f"     nodes: {nx.number_of_nodes(self)}\n"
        res += f"     edges: {nx.number_of_edges(self)}\n"
        res += f"components: {nx.number_connected_components(self)}\n"
        res += f" connected: {nx.is_connected(self)}\n"

        return res

    # endregion

    # region ServiceMethods

    @staticmethod
    def __get_coordinates_from_string(coordinates_string: str) -> tuple[list[float], list[float]]:
        """ function which formats (lat, long) data nicely """

        tuple_string = coordinates_string[15:]
        coordinate_strings_list = tuple_string.lstrip("( ").rstrip(") ").split(',')
        lon = []
        lat = []

        for lon_lat_pair in coordinate_strings_list:
            lon.append(float(lon_lat_pair.strip().split()[0].strip("()")))
            lat.append(float(lon_lat_pair.strip().split()[1].strip("()")))

        return lon, lat

    # endregion
