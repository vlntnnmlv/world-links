from railwaynet import *

# region WorkFlow


def init_world() -> RailwayNetContainer:
    data_path = "./data/trains.csv"
    data = pd.read_csv(data_path, sep=',', dtype=str)

    return RailwayNetContainer(data)

# endregion

# region Main


def main() -> None:
    container = init_world()

    usa_key = "USA"
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
            "BLR"
    ]
    test_key = ["UKR", "BLR", "POL"]

    g = container.get_nets(europe_key)

    g.draw(size=(40, 20))
    g.draw_degree_histogram()

    g.describe()

# endregion


if __name__ == "__main__":
    main()
