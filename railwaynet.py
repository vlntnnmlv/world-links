from functools import reduce, lru_cache
import random
from matplotlib import pyplot as plt
from statistics import mean
from sklearn import neighbors
from tqdm import tqdm
from geopy import distance
from rich.console import Console

import networkx as nx
import pandas as pd
import matplotlib
import contextlib
import pycountry
import pickle
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

class RailwayNet(nx.Graph):

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
        for index, component in enumerate(tqdm(components, desc=CALCULATING_COMPONENTS_MSG)):
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

    # endregion

class CountryNet(nx.Graph):

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

class RailwayNetContainer(dict):

    # region Constants

    CACHED_LIST_OF_NETS_PATH = "./cached/graphs_list.bz2"
    CACHED_FULL_GRAPH_PATH = "./cached/graph_full.bz2"

    # endregion

    # region Construction

    def __init__(self, graph_data: pd.DataFrame, countries_data: pd.DataFrame):
        self.graph_data = graph_data
        self.countries_data = RailwayNetContainer.__countries_dataframe2dict(countries_data)

        # sort countries by amount of railways in it
        self.countries_sorted = self.graph_data.iso3.value_counts().keys().to_list()

        # try to load cached list of nets
        # if not found, calculate
        # then init dict with graph values
        
        railway_nets = try_load_cached_file(RailwayNetContainer.CACHED_LIST_OF_NETS_PATH)
        if railway_nets is None:
            railway_nets = [RailwayNet(
                                    graph_data=self.graph_data,
                                    countries_data=self.countries_data,
                                    iso3=iso3
                                ) for iso3 in tqdm(self.countries_sorted, desc=CALCULATING_GRAPHS_MSG)]

            save_file_to_cache(railway_nets, RailwayNetContainer.CACHED_LIST_OF_NETS_PATH)
        super(RailwayNetContainer, self).__init__(zip(self.countries_sorted, railway_nets))
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
    
    def draw_country_graph(self, size: tuple[int, int] = (20, 10)):
        plt.figure(figsize=size)
        nx.draw(
                self.full_graph,
                edgelist=self.full_graph.edges,
                edge_color=[COLORS[ord(self.full_graph[u][v]['iso3'][0]) % len(COLORS)] for u, v in self.full_graph.edges],
                node_size=0,
                pos=dict(zip(self.full_graph.nodes, (node.coord for node in self.full_graph.nodes)))
            )
        nx.draw(
                self.countries_graph,
                edgelist=self.countries_graph.edges,
                edge_color='red',
                node_color=[COLORS[ord(self.countries_graph.nodes[u]['iso3'][0]) % len(COLORS)] for u in self.countries_graph.nodes],
                node_size=2,
                width=2,
                pos=dict(zip(self.countries_graph.nodes, (node.coord for node in self.countries_graph.nodes)))
            )
        plt.show()

    # endregion

    # region ServiceMethods
    
    def __get_full(self):
        # if full graph is initiated
        if self.full_graph is not None:
            return self.full_graph

        # try to load graph of all nets
        # if not found, calculate
        full_graph = try_load_cached_file(RailwayNetContainer.CACHED_FULL_GRAPH_PATH)
        if full_graph is None:
            full_graph = self.get_nets(self.countries_sorted, recalculate_centrality=False)
            save_file_to_cache(full_graph, RailwayNetContainer.CACHED_FULL_GRAPH_PATH)
        return full_graph

    def __calculate_centrality(self, g: RailwayNet):
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

def default_setup() -> RailwayNetContainer:
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

    return RailwayNetContainer(graph_data=data, countries_data=countries_data), data, countries_data

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