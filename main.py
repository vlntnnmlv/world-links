import pandas as pd
import networkx as nx

from matplotlib import pyplot as plt
from geopy import distance

#region Types

class Point:
  def __init__(self, lat : float, lon : float):
    self.lat = lat
    self.lon = lon
    self.coord = (lon, lat)
    self.coord_reverse = (lat, lon)

class RailwayNet(nx.Graph):
    def __init__(self, data : pd.DataFrame, iso3 : str = None): 
        super(RailwayNet, self).__init__()
        countryCondition = True if iso3 is None else data.iso3 == iso3
        for trail in data[countryCondition]['shape']:
            points = RailwayNet.__getCoordsFromString(trail)
            self.add_node(Point(points[1][0], points[0][0]))
            for i in range(len(points[0]) - 1):
                b = Point(points[1][i + 1], points[0][i + 1])
                a = Point(points[1][i], points[0][i])
                self.add_node(b)
                if (a != b) and \
                    (a.lat != b.lat or a.lon != b.lon):
                    self.add_edge(a, b)

    #region PublicMethods

    def draw(self, size : tuple[int, int]):
        """ function which draws train railways graph """

        d = dict(self.degree)

        plt.figure(figsize = size)
        nx.draw(self, nodelist = d.keys(), node_size = [0 for v in d.values()], pos = dict(zip(self.nodes, (node.coord for node in self.nodes))))
        plt.show()

    #endregion

    #region ServiceMethods

    def __getCoordsFromString(coords_string : str):
        """ function which formats (lat, long) data nicely """

        tuple_string = coords_string[15:]
        coords_list = tuple_string.lstrip("( ").rstrip(") ").split(',')
        for i in range(len(coords_list)):
            coords_pair = coords_list[i].strip().split()
            coords_list[i] = (float(coords_pair[0].strip("()")), float(coords_pair[1].strip("()")))
        return ([coord[0] for coord in coords_list],[coord[1] for coord in coords_list])

    #endregion


#endregion

#region Main

def main():
    data_path = "./data/trains.csv"
    data = pd.read_csv(data_path, sep=',')

    print(data.head())

    countries_sorted = data.iso3.value_counts().keys().to_list()
    usa = RailwayNet(data, "USA")
    usa.draw((40, 20))

#endregion

#region EntryPoint

if __name__ == "__main__":
    main()

#endregion
