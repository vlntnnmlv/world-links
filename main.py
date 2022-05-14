import pandas as pd
import networkx as nx

from matplotlib import pyplot as plt
from geopy import distance

# region Types

class Point:

    # region Construction

    def __init__(self, lat: float, lon: float):
        self.lat = lat
        self.lon = lon
        self.coord = (lon, lat)
        self.coord_reverse = (lat, lon)

    # endregion


class RailwayNetContainer(dict):
    def __init__(self, data: pd.DataFrame):
        self.raw_data = data
        self.countries_sorted = data.iso3.value_counts().keys().to_list()
        super(RailwayNetContainer, self).__init__(zip(self.countries_sorted, (None for _ in self.countries_sorted)))

    def add(self, iso3: str) -> bool:
        if iso3 in self.countries_sorted:
            self[iso3] = RailwayNet(self.raw_data, iso3)
            return True
        return False


class RailwayNet(nx.Graph):

    # region Construction

    def __init__(self, data: pd.DataFrame, iso3: str = None):
        super(RailwayNet, self).__init__()
        country_condition = True if iso3 is None else data.iso3 == iso3
        for trail in data[country_condition]['shape']:
            points = RailwayNet.__get_coordinates_from_string(trail)
            self.add_node(Point(points[1][0], points[0][0]))
            for i in range(len(points[0]) - 1):
                b = Point(points[1][i + 1], points[0][i + 1])
                a = Point(points[1][i], points[0][i])
                self.add_node(b)
                if (a != b) and \
                        (a.lat != b.lat or a.lon != b.lon):
                    self.add_edge(a, b)
    # endregion

    # region PublicMethods

    def draw(self, size : tuple[int, int]):
        """ function which draws train railways graph """

        plt.figure(figsize=size)
        nx.draw(
            self,
            nodelist=self.nodes,
            node_size=[0 for v in self.nodes],
            pos=dict(zip(self.nodes, (node.coord for node in self.nodes)))
        )
        plt.show()

    # endregion

    # region ServiceMethods

    @staticmethod
    def __get_coordinates_from_string(coordinates_string: str) -> tuple[list[float], list[float]]:
        """ function which formats (lat, long) data nicely """

        tuple_string = coordinates_string[15:]
        coordinates_list = tuple_string.lstrip("( ").rstrip(") ").split(',')
        for i in range(len(coordinates_list)):
            coordinates_pair = coordinates_list[i].strip().split()
            coordinates_list[i] = (coordinates_pair[0].strip("()"), coordinates_pair[1].strip("()"))

        return [float(coord[0]) for coord in coordinates_list], [float(coord[1]) for coord in coordinates_list]

    # endregion


# endregion

# region Main

def main() -> None:
    data_path = "./data/trains.csv"
    data = pd.read_csv(data_path, sep=',', dtype=str)

    print(data.head())

    container = RailwayNetContainer(data)
    container.add("USA")

    container["USA"].draw((40, 20))

# endregion

# region EntryPoint


if __name__ == "__main__":
    main()

# endregion
