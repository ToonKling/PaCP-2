import regex as re
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict

def read_from_file(path: str):
    pattern = r'^(\d+)\s+(\d+)\s+(\w+\s\w+)\s+(\w+)\s+([\dA-F]+)\s+([\da-fx]+)\s+((\d*))\s+\(([\d,\s]+)\)$'
    row_list = []

    with open(path, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
        for line in lines:
            match = re.match(pattern, line.strip())

            if match:
                row = {
                    '#': int(match.group(1)),
                    'thread': int(match.group(2)),
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

def get_pos(node_id: int) -> tuple[int, int]:
    return (node_id, data[data['#'] == node_id]['thread'].iloc[0])


def create_graph(to = None, fr = None):
    G = nx.DiGraph()

    edge_labels = {}

    # rf edges
    for (x, y) in rf_edges:
        G.add_node(x)
        G.add_node(y)
        G.add_edge(x, y, color='black')
        edge_labels[(x, y)] = 'rf'

    for (x, y) in hb_edges:
        G.add_node(x)
        G.add_node(y)
        G.add_edge(x, y, color='black')
        edge_labels[(x, y)] = 'hb'

    for (x, y) in swa_relation:
        G.add_node(x)
        G.add_node(y)
        G.add_edge(x, y, color='black')
        edge_labels[(x, y)] = 'swa'

    if to is not None and fr is not None:
        G.remove_edge(to, fr)
        G.add_edge(to, fr, color='red')

    # Giant mess with the types, oops
    print(f'Nodes: {G.nodes(data=True)}')
    pos = {i: get_pos(i) for (i, _) in G.nodes(data=True)}
    colors = [G[u][v]['color'] for u, v in G.edges]
    print(f'pos: {pos}')
    nx.draw_networkx(G, pos, edge_color=colors)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
    plt.show()

data = read_from_file('./races_traces/mp.txt')

# Aleks code:
node_to_thread_nr = dict()
last_seen_thread = dict()  # thread ID to last seen instruction ID
thread_creator = []  # instruction creating a thread # TODO
# node_mem_loc = dict()  # not used atm
mem_loc_node: dict[int, set] = defaultdict(set)
not_ordered_memory_locations = set()  # relaxed or acquire
node_read = set()
node_write = set()
# po_edges: list[tuple[int, int]] = [] po_edges are always == hb edges. So whenever you want to add a po edge, just add it to HB
rf_edges: list[tuple[int, int]] = []
hb_edges: list[tuple[int, int]] = []
swa_relation: list[tuple[int, int]] = []
sw_relation: list[tuple[int, int]] = []
for row in data.itertuples(index=False):
    # print(row)
    # We identify node by its ID
    node_id: int = int(row._0)

    # Each node has a thread number:
    thread_number = row.thread
    node_to_thread_nr[node_id] = thread_number

    # Node has an instruction type: read, write, other
    instr = row._2;
    mem_loc = row.Location

    # Each node has corresponding memory location
    mem_loc_node[mem_loc].add(node_id)

    # memory ordering:
    match row.MO:
        case ('relaxed'):
            not_ordered_memory_locations.add(node_id)
        case _ :
            pass

    # Add po (hb) edges:
    if thread_number in last_seen_thread:
        hb_edges.append((last_seen_thread.get(thread_number), node_id))

    last_seen_thread[thread_number] = node_id

    match instr:
        case ('thread start'):
            if node_id == 1:
                pass # This is the starting node, we do nothing
            elif data[data['#'] == node_id-1]['Action type'].iloc[0] == 'thread create':
                swa_relation.append((node_id - 1, node_id))
            else:
                # If this is not the starting node, and the starting thread was not created right before,
                # then we atm have no reliable way of finding the swa relation. I hope this will never occur.
                raise Exception('Could not find thread creation')

        case ('thread join'): # Thread finished also get handled here, but is delayed till we find a thread join

            # Idea: Search backwards for the thread finish in the correct thread
            thread_joined = int(row.Value[2:]) # Assumption: data has a form like '0x3', then this is '3'
            all_thread_finishes = data[data['Action type'] == 'thread finish']
            thread_finish_on_right_thread = all_thread_finishes[all_thread_finishes['thread'] == thread_joined]
            thread_finish_node = int(thread_finish_on_right_thread['#'].iloc[-1])

            swa_relation.append((thread_finish_node, node_id))

            pass
        case 'atomic read':
            node_read.add(node_id)
            node_to = int(row.RF)
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
                if node_id == int(enemy) or node_to_thread_nr[int(enemy)] == thread_number:
                    continue # We only consider nodes in different threads

                # TODO: If HB path does not exist, we have a data race.
                # Maybe use a union-find struct for that? Hmmm
        
        case 'atomic read':
            pass


        case _:
            pass

        # TODO: If there is a write edge,
        #  we need to go through all nodes in that memory location and see if
        #  there is an HB path between them.

        # That means we need to have following methods:
        # Find HB path between nodes based on HB.

