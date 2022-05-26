from functools import reduce, lru_cache
from matplotlib import pyplot as plt
from statistics import mean
from tqdm import tqdm
from geopy import distance

import matplotlib
import networkx as nx
import pandas as pd
import pycountry

matplotlib.use('Qt5Agg')

# region Constants

COLORS = [
          'crimson', 'cyan',
          'darkblue', 'darkcyan', 'darkgoldenrod',
          'darkgray', 'darkgreen', 'darkkhaki',
          'darkmagenta', 'darkolivegreen', 'darkorange',
          'darkorchid', 'darkred', 'darksalmon',
          'darkseagreen', 'darkslateblue', 'darkslategray',
          'darkturquoise', 'darkviolet', 'deeppink',
          'deepskyblue', 'dimgray', 'dodgerblue',
          'firebrick', 'floralwhite', 'forestgreen',
          'fuchsia', 'gainsboro', 'ghostwhite',
          'gold', 'goldenrod', 'gray',
          'green', 'greenyellow', 'honeydew',
          'hotpink', 'indianred', 'indigo',
          'ivory', 'khaki', 'lavender',
          'lavenderblush', 'lawngreen', 'lemonchiffon',
          'lightblue', 'lightcoral', 'lightcyan',
          'lightgoldenrodyellow', 'lightgreen', 'lightgray',
          'lightpink', 'lightsalmon', 'lightseagreen',
          'lightskyblue', 'lightslategray', 'lightsteelblue',
          'lightyellow', 'lime', 'limegreen',
          'linen', 'magenta', 'maroon',
          'mediumaquamarine', 'mediumblue', 'mediumorchid',
          'mediumpurple', 'mediumseagreen', 'mediumslateblue',
          'mediumspringgreen', 'mediumturquoise', 'mediumvioletred',
          'midnightblue', 'mintcream', 'mistyrose',
          'moccasin', 'navajowhite', 'navy',
          'oldlace', 'olive', 'olivedrab',
          'orange', 'orangered', 'orchid',
          'palegoldenrod', 'palegreen', 'paleturquoise',
          'palevioletred', 'papayawhip', 'peachpuff',
          'peru', 'pink', 'plum',
          'powderblue', 'purple', 'red',
          'rosybrown', 'royalblue', 'saddlebrown',
          'salmon', 'sandybrown', 'seagreen',
          'seashell', 'sienna', 'silver',
          'skyblue', 'slateblue', 'slategray',
          'snow', 'springgreen', 'steelblue',
          'tan', 'teal', 'thistle',
          'tomato', 'turquoise', 'violet',
          'wheat', 'white', 'whitesmoke',
          'yellow', 'yellowgreen'
          ]

# endregion

# region Types

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
    
    # enderegions

    # region OverloadMethods

    def __eq__(self, other):
        return self.lat == other.lat and self.lon == other.lon

    def __hash__(self):
        return hash(self.coord)

    # endregion

class RailwayNet(nx.Graph):

    # region Construction

    def __init__(self, data: pd.DataFrame = None, capitals: dict[str, Point] = None, max_speed: float = None, iso3: str = None):
        super(RailwayNet, self).__init__()

        self.countries = set()

        if data is not None:
            if iso3 is not None:
                self.countries.add(iso3)

            data_filtered = data if iso3 is None else data[data.iso3 == iso3]
            for trail in data_filtered['shape']:
                lat, lon = RailwayNet.__get_coordinates_from_string(trail)
                self.add_node(Point(lon[0], lat[0]), iso3=iso3)
                for i in range(len(lat) - 1):
                    b = Point(lon[i + 1], lat[i + 1])
                    a = Point(lon[i], lat[i])
                    self.add_node(b, iso3=iso3)
                    if a.lat != b.lat or a.lon != b.lon:
                        self.add_edge(
                                a,
                                b,
                                distance=a.distance(b),
                                centrality=a.distance(capitals[iso3]),
                                speed=80 if max_speed is None else max_speed,
                                iso3=iso3
                            )

    # endregion

    # region PublicMethods

    @lru_cache(maxsize=None)
    def get_biggest_component(self):
        return self.subgraph(max(nx.connected_components(self), key=len))

    def draw_countries(self, size: tuple[int, int] = (20, 10, )):
        plt.figure(figsize=size)
        nx.draw(
                self,
                edgelist=self.edges,
                edge_color=[COLORS[ord(self[u][v]['iso3'][0]) % len(COLORS)] for u, v in self.edges],
                node_size=0,
                pos=dict(zip(self.nodes, (node.coord for node in self.nodes)))
            )
        plt.show()
    
    def draw_components(self, size: tuple[int, int] = (20, 10)):
        plt.figure(figsize=size)
        components = sorted(nx.connected_components(self), key=len, reverse=True)[:20]
        for index, component in enumerate(tqdm(components)):
            subgraph = self.subgraph(component)
            nx.draw(
                subgraph,
                edgelist=subgraph.edges,
                edge_color=COLORS[index % (len(COLORS))],
                node_size=0,
                pos=dict(zip(subgraph.nodes, (node.coord for node in subgraph.nodes)))
            )
        plt.show()

    def draw_by_attribute(self, attr: str, size: tuple[int, int] = (20, 10), separate_countries: bool = False):

        def green2red(ratio: float) -> tuple[float, float, float]:
            return (ratio, 1 - ratio, 0)

        plt.figure(figsize=size)

        if separate_countries:
            for country in self.countries:
                subgraph = self.subgraph([node for node in self.nodes if self.nodes[node]['iso3'] == country])
                attr_list = [self[u][v][attr] for u,v in subgraph.edges]
                attr_max  = max(attr_list)
                nx.draw(
                        subgraph,
                        edgelist=subgraph.edges,
                        edge_color=[green2red(attr/attr_max) for attr in attr_list],
                        node_size=0,
                        pos=dict(zip(subgraph.nodes, (node.coord for node in subgraph.nodes)))
                    )
        else:
            attr_list = [self[u][v][attr] for u,v in self.edges]
            attr_max  = max(attr_list)
            nx.draw(
                    self,
                    edgelist=self.edges,
                    edge_color=[green2red(attr/attr_max) for attr in attr_list],
                    node_size=0,
                    pos=dict(zip(self.nodes, (node.coord for node in self.nodes)))
                )
        plt.show()

    def draw_degree_histogram(self):
        plt.hist(nx.degree_histogram(self))
        plt.show()

    def describe(self) -> None:
        res = "\n"
        res += f"                   nodes: {nx.number_of_nodes(self)}\n"
        res += f"                   edges: {nx.number_of_edges(self)}\n"
        res += f"              components: {nx.number_connected_components(self)}\n"
        res += f"               connected: {nx.is_connected(self)}\n"

        biggest_component_part = nx.number_of_nodes(self.get_biggest_component()) / nx.number_of_nodes(self)
        res += f"  biggest component part: {biggest_component_part:.6}\n"

        print(res)

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

    @staticmethod
    def __calculate_centrality(p: Point, iso3: str, capitals: dict[str, Point]) -> float:
        nearest3capitals = dict()
        for country, capital in capitals.items():
            dist = p.distance(capital)
            if (len(nearest3capitals) < 3):
                nearest3capitals[country] = dist
            elif any([p.distance(capital) < d for d in nearest3capitals.values()]):
                max_dist_country = max(nearest3capitals, key=nearest3capitals.get)
                del nearest3capitals[max_dist_country]
                nearest3capitals[country] = dist

        if (all([dist > 500 for dist in nearest3capitals.values()])):
            return p.distance(capitals[iso3])

        return mean([dist for dist in nearest3capitals.values() if dist <= 500])

    # endregion

class RailwayNetContainer(dict):

    # region Construction

    def __init__(self, data: pd.DataFrame, capitals_data: pd.DataFrame, speed_data: pd.DataFrame):
        self.raw_data = data
        self.countries_sorted = data.iso3.value_counts().keys().to_list()

        self.capitals_data = capitals_data
        self.capitals_data = self.capitals_data[self.capitals_data.CountryCode.isin(self.countries_sorted)].reset_index().drop(columns=["index"])
        self.countries_sorted = list(filter(lambda c: c in list(self.capitals_data.CountryCode), self.countries_sorted))
        self.capitals_data = dict(
            zip(
                list(self.capitals_data.CountryCode),
                [self.get_capital(iso3) for iso3 in self.capitals_data.CountryCode]
                )
            )

        self.speed_data = speed_data

        super(RailwayNetContainer, self).__init__(zip(self.countries_sorted, (None for _ in self.countries_sorted)))

    # endregion

    # region PublicMethods

    def get_net(self, iso3: str) -> RailwayNet | None:
        if iso3 in self.countries_sorted:
            if self[iso3] is None:
                self[iso3] = RailwayNet(
                    self.raw_data,
                    capitals=self.capitals_data,
                    max_speed=self.get_speed(iso3=iso3),
                    iso3=iso3
                    )
            return self[iso3]
        return None

    def get_nets(self, iso3_lst: list[str]) -> RailwayNet | None:
        res = RailwayNet()

        def compose(G, H):
            C = nx.compose(G, H)
            C.countries = G.countries.union(H.countries)
            return C

        res = reduce(compose, tqdm([self.get_net(iso3) for iso3 in iso3_lst if iso3 in self.countries_sorted]), res)
        return res if nx.number_of_nodes(res) > 0 else None

    def get_capital(self, iso3: str) -> Point:
        row = self.capitals_data[self.capitals_data.CountryCode == iso3].iloc[0]
        return Point(row.CapitalLatitude, row.CapitalLongitude)

    def get_speed(self, iso3: str) -> float:
        return float(self.speed_data[self.speed_data.CountryCode == iso3].iloc[0].MaximumTrainSpeed)

    # endregion

# endregion

# region Functions

def default_setup() -> RailwayNetContainer:
    data_path = "./data/trains.csv"
    capitals_data_path = "./data/country_capitals.csv"
    speed_data_path="./data/train_speed.csv"

    data = pd.read_csv(data_path, sep=',', dtype=str)[["iso3", "shape"]]

    capitals_data = pd.read_csv(capitals_data_path, sep=',').dropna()[["CountryCode", "CapitalLatitude", "CapitalLongitude"]]
    capitals_data.CountryCode = capitals_data.CountryCode.apply(lambda c : pycountry.countries.get(alpha_2 = c).alpha_3 if pycountry.countries.get(alpha_2 = c) is not None else None)

    speed_data = pd.read_csv(speed_data_path, sep=',')
    speed_data['CountryCode'] = speed_data.CountryName.apply(lambda name: pycountry.countries.search_fuzzy(name)[0].alpha_3)
    speed_data = speed_data.drop(columns=["CountryName"])

    return RailwayNetContainer(data=data, capitals_data=capitals_data, speed_data=speed_data), data, capitals_data

def test_graph() -> RailwayNet:
    c, _, _ = default_setup()
    europe_key = [
            "AUT",
            "BEL",
            "BGR",
            "HRV",
            "CZE",
            "DNK",
            "EST",
            "FIN",
            "FRA",
            "DEU",
            "GRC",
            "HUN",
            "ITA",
            "LVA",
            "LTU",
            "LUX",
            "NLD",
            "POL",
            "PRT",
            "ROU",
            "SVK",
            "SVN",
            "ESP",
            "SVE",
            "UKR",
            "BLR",
            "RUS"
    ]
    return c.get_nets(["UKR", "POL", "BLR"])

# endregion