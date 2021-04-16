import networkx
import networkx.algorithms.shortest_paths
G = networkx.Graph()

G.add_edge('PINK_START', 'PINK_TOP_CORNER')
G.add_edge('PINK_START', 'BOTTOM_LEFT_CORNER')
G.add_edge('YELLOW_START', 'BOTTOM_RIGHT_CORNER')
G.add_edge('YELLOW_START', 'YELLOW_TOP_CORNER')
G.add_edge('BOTTOM_CENTRE_UPPER', 'BOTTOM_LEFT_LOWER')
G.add_edge('BOTTOM_CENTRE_UPPER', 'BOTTOM_RIGHT_LOWER')
G.add_edge('BOTTOM_CENTRE_LOWER', 'BOTTOM_LEFT_LOWER')
G.add_edge('BOTTOM_CENTRE_UPPER', 'BOTTOM_RIGHT_LOWER')
G.add_edge('BOTTOM_LEFT_LOWER', 'BOTTOM_LEFT_UPPER')
G.add_edge('BOTTOM_RIGHT_LOWER', 'BOTTOM_RIGHT_UPPER')
G.add_edge('BOTTOM_LEFT_UPPER', 'BOTTOM_CENTRE_LOWER')
G.add_edge('BOTTOM_RIGHT_UPPER', 'BOTTOM_CENTRE_LOWER')
G.add_edge('BOTTOM_LEFT_UPPER', 'LEFT_TRANSITION')
G.add_edge('BOTTOM_RIGHT_UPPER', 'RIGHT_TRANSITION')
G.add_edge('BOTTOM_LEFT_CORNER', 'BOTTOM_LEFT_LOWER')
G.add_edge('BOTTOM_RIGHT_CORNER', 'BOTTOM_RIGHT_LOWER')
G.add_edge('BOTTOM_CENTRE_LOWER', 'BOTTOM_CENTRE_UPPER')
G.add_edge('BOTTOM_LEFT_UPPER', 'BOTTOM_CENTRE_UPPER')
G.add_edge('BOTTOM_RIGHT_UPPER', 'BOTTOM_CENTRE_UPPER')
G.add_edge('LEFT_TRANSITION', 'TOP_LEFT')
G.add_edge('RIGHT_TRANSITION', 'TOP_RIGHT')
G.add_edge('TOP_LEFT', 'TOP_CENTRE')
G.add_edge('TOP_RIGHT', 'TOP_CENTRE')

def print_graph(name, graph):
    print("%s = {" % name)
    for origin, paths in networkx.algorithms.shortest_paths.all_pairs_shortest_path(graph):
        for dest, path in paths.items():
            if origin == dest:
                continue
            print(f"    (Zone.{origin}, Zone.{dest}): Zone.{path[1]},")
    print("}")
    print("")

print_graph("ROUTING_PRE_DROP", G)

G.add_edge('PINK_START', 'LEFT_TRANSITION')
G.add_edge('PINK_START', 'TOP_LEFT')
G.add_edge('PINK_TOP_CORNER', 'LEFT_TRANSITION')
G.add_edge('PINK_TOP_CORNER', 'TOP_LEFT')
G.add_edge('BOTTOM_LEFT_CORNER', 'LEFT_TRANSITION')
G.add_edge('BOTTOM_LEFT_LOWER', 'LEFT_TRANSITION')
G.add_edge('BOTTOM_LEFT_CORNER', 'BOTTOM_LEFT_UPPER')

G.add_edge('YELLOW_START', 'RIGHT_TRANSITION')
G.add_edge('YELLOW_START', 'TOP_RIGHT')
G.add_edge('YELLOW_TOP_CORNER', 'RIGHT_TRANSITION')
G.add_edge('YELLOW_TOP_CORNER', 'TOP_RIGHT')
G.add_edge('BOTTOM_RIGHT_CORNER', 'RIGHT_TRANSITION')
G.add_edge('BOTTOM_RIGHT_LOWER', 'RIGHT_TRANSITION')
G.add_edge('BOTTOM_RIGHT_CORNER', 'BOTTOM_RIGHT_UPPER')

print_graph("ROUTING_POST_DROP", G)
