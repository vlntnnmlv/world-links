from railwaynet import *

# region WorkFlow


def init_world() -> RailwayNetContainer:
    data_path = "./data/trains.csv"
    data = pd.read_csv(data_path, sep=',', dtype=str)

    return RailwayNetContainer(data, pd.read_csv("./data/country_capitals"))

# endregion

# region Main

def main() -> None:
    container, data, capitals_data = default_setup()

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
            "BLR",
            "RUS",
            "GBR"
    ]
    # test_key = ["UKR", "BLR", "POL"]

    # g = container.get_nets(test_key)
    # g.draw_by_attribute("centrality")

    container.draw_country_graph()

    # g.describe()

# endregion


if __name__ == "__main__":
    main()
