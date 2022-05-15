from railwaynet import *

# region WorkFlow


def init() -> RailwayNetContainer:
    data_path = "./data/trains.csv"
    data = pd.read_csv(data_path, sep=',', dtype=str)

    return RailwayNetContainer(data)

# endregion

# region Main


def main() -> None:
    container = init()
    g = container.get_net("USA")

    g.draw(size=(40, 20), show_components=True)
    g.describe()

# endregion


if __name__ == "__main__":
    main()
