from railwaynet import *
from editor import *
# region Main

def main() -> None:
    container, _, _ = default_setup()

    g = container.get_nets(["UKR"])
    editor = Editor(g.get_points_dataframe())
    editor.run()
    # g = container.countries_graph

    # frm = None
    # to = None
    # for node in g.nodes:
    #     if g.nodes[node]['iso3'] == "RUS":
    #         frm = node
    #     if g.nodes[node]['iso3'] == "PRT":
    #         to = node

    # path = nx.dijkstra_path(g, frm, to, "distance")
    # p = g.subgraph(path)

    # nx.draw(g, edgelist=g.edges, node_size=0, pos=dict(zip(g.nodes, [node.coord for node in g.nodes])))
    # nx.draw(p, edgelist=p.edges, edge_color='red', node_size=1, pos=dict(zip(p.nodes, [node.coord for node in p.nodes])))
    # plt.show()

# endregion


if __name__ == "__main__":
    main()
