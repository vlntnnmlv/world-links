from functools import reduce, lru_cache
from matplotlib import pyplot as plt
from rich.console import Console
from geograph import GeoGraph, Point
from statistics import mean
from tqdm import tqdm

import networkx as nx
import pandas as pd
import matplotlib
import contextlib
import pycountry
import pickle
import random
import bz2

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

CONSOLE = Console()

CALCULATING_COMPONENTS_MSG = "Calculating components"
CALCULATING_GRAPHS_MSG     = "    Calculating graphs"
COMBINING_GRAPHS_MSG       = "       Combinig graphs"
CALCULATING_CENTRALITY_MSG = "Calculating centrality"

PROGRESS_BAR_WIDTH = 100

# endregion

# region Types  

class RailwayNet(GeoGraph):

    # region Construction

    def __init__(self, graph_data: pd.DataFrame = None, countries_data: pd.DataFrame = None, iso3: str = None):
        super(RailwayNet, self).__init__()

        self.countries = set()

        if graph_data is not None:
            if iso3 is not None:
                self.countries.add(iso3)

            data_filtered = graph_data if iso3 is None else graph_data[graph_data.iso3 == iso3]
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
                                centrality=a.distance(countries_data[iso3]['capital']),
                                speed=80 if countries_data is None else countries_data[iso3]['speed'],
                                iso3=iso3
                            )

    # endregion

    # region PublicMethods

    @lru_cache(maxsize=None)
    def get_biggest_component(self):
        return self.subgraph(max(nx.connected_components(self), key=len))

    def get_points_dataframe(self):
        points_dataframe = pd.DataFrame(
            {
                'lat':  [node.coord_reverse[0] for node in self.nodes],
                'lon':  [node.coord_reverse[1] for node in self.nodes],
                'iso3': [self.nodes[node]['iso3'] for node in self.nodes]
            }
        )
        return points_dataframe

    def draw_plot_by_country(self, size: tuple[int, int] = (20, 10, ), ):
        plt.figure(figsize=size)
        edge_color=[COLORS[ord(self[u][v]['iso3'][0]) % len(COLORS)] for u, v in self.edges]
        self.draw(edge_color=edge_color, node_size=0)
    
    def draw_plot_by_component(self, size: tuple[int, int] = (20, 10)):
        plt.figure(figsize=size)
        components = sorted(nx.connected_components(self), key=len, reverse=True)[:20]
        for index, component in enumerate(tqdm(components, desc=CALCULATING_COMPONENTS_MSG)):
            self.subgraph(component).draw(edge_color=COLORS[index % (len(COLORS))], node_size=0)

    def draw_plot_by_attribute(self, attr: str, size: tuple[int, int] = (20, 10)):

        def green2red(ratio: float) -> tuple[float, float, float]:
            return (ratio, 1 - ratio, 0)

        plt.figure(figsize=size)
        attr_list = [self[u][v][attr] for u,v in self.edges]
        min_attr = min(attr_list)
        ratio_derivative = max(attr_list) - min_attr
        self.draw(edge_color=[green2red((attr - min_attr)/ratio_derivative) for attr in attr_list], node_size=0)

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

    # endregion

class PathEdgePoint:
    def __init__(self, point: Point, iso3: str):
        self.point = point
        self.iso3 = iso3

    def __eq__(self, other):
        if other is None:
            return False
        return self.point == other.point and other.iso3 == other.iso3 

class CountryNet(GeoGraph):

    # region Construction

    def __init__(self, countries_data: dict = None):
        super(CountryNet, self).__init__()

        if countries_data is not None:
           for country, country_attributes in countries_data.items():
               self.add_node(country_attributes['capital'], iso3 = country)
               for neighbour in country_attributes['neighbours']:
                   if neighbour == country:
                       continue
                   self.add_edge(
                        country_attributes['capital'],
                        countries_data[neighbour]['capital'],
                        distance=country_attributes['capital'].distance(countries_data[neighbour]['capital']),
                        speed=80,
                        )

    # endregion

class RailwayNetManager(dict):

    # region Constants

    CACHED_LIST_OF_NETS_PATH = "./cached/graphs_list.bz2"
    CACHED_FULL_GRAPH_PATH = "./cached/graph_full.bz2"

    # endregion

    # region Construction

    def __init__(self, graph_data: pd.DataFrame, countries_data: pd.DataFrame):
        self.graph_data = graph_data
        self.countries_data = RailwayNetManager.__countries_dataframe2dict(countries_data)

        self.start_node = None
        self.finish_node = None

        # sort countries by amount of railways in it
        self.countries_sorted = self.graph_data.iso3.value_counts().keys().to_list()

        # try to load cached list of nets
        # if not found, calculate
        # then init dict with graph values
        railway_nets = try_load_cached_file(RailwayNetManager.CACHED_LIST_OF_NETS_PATH)
        if railway_nets is None:
            railway_nets = [RailwayNet(
                                    graph_data=self.graph_data,
                                    countries_data=self.countries_data,
                                    iso3=iso3
                                ) for iso3 in tqdm(self.countries_sorted, desc=CALCULATING_GRAPHS_MSG)]

            save_file_to_cache(railway_nets, RailwayNetManager.CACHED_LIST_OF_NETS_PATH)
        super(RailwayNetManager, self).__init__(zip(self.countries_sorted, railway_nets))
        self.full_graph = None
        self.full_graph = self.__get_full()

        for country in self.countries_data:
            self.countries_data[country]['neighbours'] = set()
            self.countries_data[country]['neighbours'].add(country)

        for edge in self.full_graph.edges:
            a_country = self.full_graph.nodes[edge[0]]['iso3']
            b_country = self.full_graph.nodes[edge[1]]['iso3']
            if a_country != b_country:
                self.countries_data[a_country]['neighbours'].add(b_country)

        self.countries_graph = CountryNet(self.countries_data)

    # endregion

    # region PublicMethods

    def get_random(self):
        countries_number = random.randrange(1, len(self.countries_sorted + 1))
        countries_list = []
        while len(countries_list) != countries_number:
            country_chosen = random.choice(self.countries_sorted)
            if country_chosen not in countries_list:
                countries_list.append(country_chosen)

        return self.get_nets(countries_list)

    def get_net(self, iso3: str) -> RailwayNet | None:
        if iso3 in self.countries_sorted:
            if self[iso3] is None:
                self[iso3] = RailwayNet(
                    self.graph_data,
                    countries_data=self.countries_data,
                    iso3=iso3
                    )
            return self[iso3]
        return None

    def get_nets(self, iso3_lst: list[str], recalculate_centrality: bool = True) -> RailwayNet | None:
        res = RailwayNet()

        def compose(G, H):
            C = nx.compose(G, H)
            C.countries = G.countries.union(H.countries)
            return C

        res = reduce(compose, tqdm([self.get_net(iso3) for iso3 in iso3_lst if iso3 in self.countries_sorted], desc=COMBINING_GRAPHS_MSG), res)
        if nx.number_of_nodes(res) <= 0:
            return None

        if recalculate_centrality:
            self.__calculate_centrality(res)
        return res

    def save_node(self, point: tuple[float, float], iso3: str) -> bool:
        for node in self.full_graph.nodes:
            if node.coord == point:
                if self.start_node is None:
                    self.start_node = PathEdgePoint(node, iso3)
                    return True
                elif self.finish_node is None:
                    self.finish_node = PathEdgePoint(node, iso3)
                    return True
                return False
        return False

    def find_path(self):
        if self.start_node == None or self.finish_node == None:
            return False
        
        if self.start_node.iso3 == self.finish_node.iso3:
            return nx.dijkstra_path(
                self.full_graph.get_biggest_component(),
                self.start_node.point,
                self.finish_node.point,
                "distance")
        
        else:
            frm = None
            to = None
            for n in self.countries_graph.nodes:
                if self.countries_graph.nodes[n]['iso3'] == self.start_node.iso3:
                    frm = n
                if self.countries_graph.nodes[n]['iso3'] == self.finish_node.iso3:
                    to = n
            cpath = nx.dijkstra_path(self.countries_graph, frm, to, "distance")
            countries_in_path = []
            for p in cpath:
                for n in self.countries_graph.nodes:
                    if n == p:
                        countries_in_path.append(self.countries_graph.nodes[n]['iso3'])
            g = self.get_nets(countries_in_path)
            path = nx.dijkstra_path(
                g,
                self.start_node.point,
                self.finish_node.point,
                "distance")
            print(f"Path found {len(path)}")
            return path

    # endregion

    # region ServiceMethods
    
    def __get_full(self) -> RailwayNet:
        # if full graph is initiated
        if self.full_graph is not None:
            return self.full_graph

        # try to load graph of all nets
        # if not found, calculate
        full_graph = try_load_cached_file(RailwayNetManager.CACHED_FULL_GRAPH_PATH)
        if full_graph is None:
            full_graph = self.get_nets(self.countries_sorted, recalculate_centrality=False)
            save_file_to_cache(full_graph, RailwayNetManager.CACHED_FULL_GRAPH_PATH)
        return full_graph

    def __calculate_centrality(self, g: RailwayNet) -> None:
        for edge in tqdm(g.edges, desc=CALCULATING_CENTRALITY_MSG):
            g.edges[edge]['centrality'] = \
                mean(
                    (edge[0].distance(self.countries_data[neighbour]['capital']) \
                        for neighbour in \
                            self.countries_data[g.edges[edge]['iso3']]['neighbours']))

    @staticmethod
    def __countries_dataframe2dict(countries_data: pd.DataFrame) -> dict:
        countries_dict = dict()
        for iso3 in countries_data.iso3:
            country = countries_data[countries_data.iso3 == iso3].iloc[0]
            countries_dict[iso3] = {
                'speed'   : country.MaximumTrainSpeed,
                'capital' : Point(country.CapitalLatitude, country.CapitalLongitude)
                }
        return countries_dict

    # endregion

# endregion

# region Functions

def default_setup() -> RailwayNetManager:
    # manage graph data
    data_path = "./data/trains.csv"
    data = pd.read_csv(data_path, sep=',', dtype=str)[["iso3", "shape"]]

    # manage countries data
    capitals_data_path = "./data/country_capitals.csv"
    capitals_data = pd.read_csv(capitals_data_path, sep=',').dropna()[['CountryCode', 'CapitalLatitude', 'CapitalLongitude']]
    capitals_data['iso3'] = capitals_data.CountryCode.apply(lambda c : pycountry.countries.get(alpha_2 = c).alpha_3 if pycountry.countries.get(alpha_2 = c) is not None else None)
    capitals_data = capitals_data.drop(columns=['CountryCode'])

    speed_data_path="./data/train_speed.csv"
    speed_data = pd.read_csv(speed_data_path, sep=',')
    speed_data['iso3'] = speed_data.CountryName.apply(lambda name: pycountry.countries.search_fuzzy(name)[0].alpha_3)
    speed_data = speed_data.drop(columns=['CountryName'])

    # merge countries
    countries_data = speed_data.merge(capitals_data)

    # synchronize graph data by available countries data
    data = data[data.iso3.isin(countries_data.iso3)]

    return RailwayNetManager(graph_data=data, countries_data=countries_data), data, countries_data

def try_load_cached_file(path: str):
    data = None
    try:
        with CONSOLE.status(f"Loading {path} file"), contextlib.closing(bz2.BZ2File(path, 'rb')) as f:
            print(f"File '{path}' found")
            data = pickle.load(f)
    except FileNotFoundError as e:                
        print(e)

    return data

def save_file_to_cache(obj, path: str):
    with contextlib.closing(bz2.BZ2File(path, 'wb')) as f:
                pickle.dump(obj, f) 

# endregion