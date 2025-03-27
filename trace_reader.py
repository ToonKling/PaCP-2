import regex as re
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

def read_from_file(path: str):
    pattern = r'^(\d+)\s+(\d+)\s+(\w+\s\w+)\s+(\w+)\s+([\dA-F]+)\s+([\da-fx]+)\s+((\d*))\s+\(([\d,\s]+)\)$'
    row_list = []

    with open(path, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
        for line in lines:
            match = re.match(pattern, line.strip())

            if match:
                row = {
                    '#': match.group(1),
                    'thread': match.group(2),
                    'Action type': match.group(3).strip(),
                    'MO': match.group(4),
                    'Location': match.group(5),
                    'Value': match.group(6),
                    'RF': match.group(7) if match.group(7) else ''
                }
                row_list.append(row)
            else:
                raise RuntimeError('unexpected line format')
    return pd.DataFrame(row_list)


def create_graph(to, fr):
    G = nx.DiGraph()

    edge_labels = {}

    # rf edges
    for (x, y) in rf_edges:
        G.add_node(x)
        G.add_node(y)
        G.add_edge(x, y)
        edge_labels[(x, y)] = 'rf'

    for (x, y) in hb_edges:
        G.add_node(x)
        G.add_node(y)
        G.add_edge(x, y)
        edge_labels[(x, y)] = 'hb'

    edge_labels[(to, fr)] += ', race'

    # Giant mess with the types, oops
    print(f'Nodes: {G.nodes(data=True)}')
    pos = {i: [int(data['#'][int(i)]), int(data['thread'][int(i)])] for (i, _) in G.nodes(data=True)}
    print(f'pos: {pos}')
    nx.draw_networkx(G, pos)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
    plt.show()

data = read_from_file('./races_traces/mp2.txt')

# Aleks code:
node_to_thread_nr = dict()
last_seen_thread = dict()  # thread ID to last seen instruction ID
thread_creator = []  # instruction creating a thread # TODO
# node_mem_loc = dict()  # not used atm
mem_loc_node: dict[int, set] = dict()
not_ordered_memory_locations = set()  # relaxed or acquire
node_read = set()
node_write = set()
# po_edges: list[tuple[int, int]] = [] po_edges are always == hb edges. So whenever you want to add a po edge, just add it to HB
rf_edges: list[tuple[int, int]] = []
hb_edges: list[tuple[int, int]] = []
start_join_create_nodes = set() # TODO handling

for row in data.itertuples(index=False):
    # print(row)
    # We identify node by its ID
    node_id = row._0

    # Each node has a thread number:
    thread_number = row.thread
    node_to_thread_nr[node_id] = thread_number

    # Node has an instruction type: read, write, other
    instr = row._2;
    mem_loc = row.Location

    # Each node has corresponding memory location
    if mem_loc in mem_loc_node:
        mem_loc_node.get(mem_loc).add(node_id)
    else:
        mem_loc_node[mem_loc] = set(node_id)

    # memory ordering:
    mo = row.MO
    match mo:
        case ('relaxed' | 'acquire'):
            not_ordered_memory_locations.add(node_id)
        case _ :
            pass

    # Add po (hb) edges:
    if thread_number in last_seen_thread:
        hb_edges.append((last_seen_thread.get(thread_number), node_id))

    last_seen_thread[thread_number] = node_id

    match instr:
        case ('thread start' | 'thread create' | 'thread join' | 'thread finish'):
            # TODO: Handle those cases. Figure out how to add HB edges here.
            start_join_create_nodes.add(node_id)
        case 'atomic read':
            node_read.add(node_id)
            node_to = row.RF
            rf_edges.append((node_id, node_to))  # Created an RF edge

            # Create an HB edge:
            if node_id not in not_ordered_memory_locations and \
                    node_to not in not_ordered_memory_locations:
                hb_edges.append((node_to, node_id))
            elif node_to in node_write: # I think this already meets conditions for a data race.
                print(f"DATA RACE between nodes {node_to} and {node_id}")
                create_graph(node_id, node_to)
                break

        case 'atomic write':
            node_write.add(node_id)

            for enemy in mem_loc_node[mem_loc]:
                if node_id == enemy:
                    continue
                if node_to_thread_nr[enemy] == thread_number: # We only consider nodes in different threads
                    continue

                # TODO: If HB path does not exist, we have a data race.
                # Maybe use a union-find struct for that? Hmmm

        case _:
            pass

        # TODO: If there is a write edge,
        #  we need to go through all nodes in that memory location and see if
        #  there is an HB path between them.

        # That means we need to have following methods:
        # Find HB path between nodes based on HB.

