import regex as re
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict
import sys

sys.setrecursionlimit(100000)

pattern = r'^(\d+)\s+(\d+)\s+(\w+\s\w+|\w+)\s+(\w+)\s+([\dA-F]+)\s+([\da-fx]+)\s+(\([\da-f]+\))?\s+(\d*)\s+\(([\d,\s]+)\)$'


def read_from_file(path: str):
    row_list = []

    with open(path, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
        print(f'Read the lines')
        for line in lines:
            row_list.append(line)
    return pd.DataFrame(row_list)

def read_line(line):
    match = re.match(pattern, line.strip())

    if match:
        return {
            '#': int(match.group(1)),
            'thread': int(match.group(2)),
            'Action type': match.group(3).strip(),
            'MO': match.group(4),
            'Location': match.group(5),
            'Value': match.group(6),
            # group 7 is the number in brackets for rwm operations
            'RF': match.group(8) if match.group(8) else ''
        }
    else:
        raise RuntimeError(f'unexpected line format in line\n{line}')


# I don't claim this is efficient, I leave that to the algorithmics people ;)
def path_exists(hb_edges: set[tuple[int, int]], from_node: int, to_node: int) -> bool:
    lookup_table = defaultdict(set)
    for (u, v) in hb_edges:
        lookup_table[u].add(v)
    visited = set()

    def dfs(search_node: int):
        if search_node == to_node:
            return True
        if search_node in visited:
            return False
        visited.add(search_node)
        return any([dfs(neighbour) for neighbour in lookup_table[search_node]])
    return dfs(from_node)

def get_pos(data, node_id: int) -> tuple[int, int]:
    return (node_id, data[data['#'] == node_id]['thread'].iloc[0])


def create_graph(data, rf_edges, hb_edges, swa_relation, to = None, fr = None, draw_graph: bool = False):
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

    mapping = {'atomic write': 'red', 'atomic read': 'blue'}
    node_colors = [
        mapping.get(data[data['#'] == n]['Action type'].iloc[-1], "#1f78b4")
        if not data[data['#'] == n].empty else "#808080"  # Default gray for missing nodes
        for n in G.nodes
    ]
    # Giant mess with the types, oops
    # print(f'Nodes: {G.nodes(data=True)}')
    pos = {}
    for i in G.nodes:
        try:
            pos[i] = get_pos(data, i)
        except Exception as e:
            pos[i] = (0, 0)


    colors = [G[u][v]['color'] for u, v in G.edges]
    nx.draw_networkx(G, pos, edge_color=colors, node_color=node_colors[:len(pos)])
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
    plt.savefig("output.png")
    if draw_graph:
        plt.show()



def find_data_race(fileName: str, draw_graph: bool = False) -> list[tuple[int, int]]:
    # print(f'Finding the data race')
    raw_lines = read_from_file(fileName)
    # print(f'Read the file')

    node_to_thread = dict()
    last_seen_thread = dict()  # thread ID to last seen instruction ID
    latest_release_write: dict[str, int] = defaultdict(int) # {memory location : node_id}
    # list of release sequences that ended with an acquire
    acquire_to_release: dict[int, int] = dict() # from acquire to release according to release sequence
    # {node - sequqnce} map with sequences that are not complete or broken yet
    ongoing_release_sequences: dict[int, list[int]] = dict()
    not_ordered_memory_locations = set()  # relaxed
    node_write = set()
    sb_relations: set[tuple[int, int]] = set()
    rf_relations: set[tuple[int, int]] = set()
    sw_relations: set[tuple[int, int]] = set()
    hb_relations: set[tuple[int, int]] = set()

    data_races = []

    parsed_rows = []
    for row_raw in raw_lines.itertuples(index=False):
        row = read_line(row_raw._0)
        parsed_rows.append(row)
        data = pd.DataFrame(parsed_rows)
        node_id: int = int(row['#'])
        thread_id = row['thread']
        node_to_thread[node_id] = thread_id
        instr = row['Action type'];
        mem_loc = row['Location']

        # memory ordering:
        if row['MO'] == 'relaxed':
            not_ordered_memory_locations.add(node_id)

        if thread_id in last_seen_thread:
            sb_relations.add((last_seen_thread.get(thread_id), node_id))
        last_seen_thread[thread_id] = node_id

        match instr:
            case 'thread start':
                if node_id == 1:
                    pass # This is the starting node, we do nothing
                elif data[data['#'] == node_id-1]['Action type'].iloc[0] in ['thread create', 'pthread create']:
                    sw_relations.add((node_id - 1, node_id)) # adding an asw relation
                else:
                    # If this is not the starting node, and the starting thread was not created right before,
                    # then we atm have no reliable way of finding the swa relation. I hope this will never occur.
                    raise Exception('Could not find thread creation')
            
            case 'thread join': # Thread finished also get handled here, but is delayed till we find a thread join

                # Idea: Search backwards for the thread finish in the correct thread
                thread_joined = int(row['Value'], 16) # Assumption: data has a form like '0x3', then this is '3'
                all_thread_finishes = data[data['Action type'] == 'thread finish']
                thread_finish_on_right_thread = all_thread_finishes[all_thread_finishes['thread'] == thread_joined]
                thread_finish_node = int(thread_finish_on_right_thread['#'].iloc[-1])
                sw_relations.add((thread_finish_node, node_id)) # adding an asw relation

                pass
            
            case 'atomic read':
                node_from = int(row['RF'])
                rf_relations.add((node_from, node_id))  # Created an RF edge
                if node_id == 8:
                    print(row['RF'], latest_release_write[mem_loc])
                if row['MO'] == 'acquire' and mem_loc in latest_release_write.keys() and int(row['RF']) == latest_release_write[mem_loc]:
                    # to my understanding, only consume finishes the release sequence
                    start_node = latest_release_write[mem_loc]
                    ongoing_release_sequences[start_node].append(node_id)
                    acquire_to_release[node_id] = start_node
                    if thread_id != node_to_thread[start_node]:
                        sw_relations.add((start_node, node_id)) # add sw edge as release/acquire synchronization case 1
                    # if acquire read never concludes release sequence, no cleanup is needed
                    # del ongoing_release_sequences[start_node]
                    # del latest_release_write[mem_loc]
                if node_from in acquire_to_release:
                    sw_relations.add((acquire_to_release[node_id], node_id))# add sw edge as release/acquire synchronization case 2
    
            case 'atomic write':
                node_write.add(node_id)
                if row['MO'] == 'release' and mem_loc not in latest_release_write:
                        latest_release_write[mem_loc] = node_id
                        ongoing_release_sequences[node_id] = [node_id]
                elif mem_loc in latest_release_write:
                    # any write from the same thread continues release sequence
                    start_node = latest_release_write[mem_loc]
                    if start_node != 0 and node_to_thread[start_node] == thread_id:
                        # here assuming that another release from the same thread will be a part of ongoing sequence
                        ongoing_release_sequences[start_node].append(node_id)
                    else:
                        if start_node != 0:
                            del ongoing_release_sequences[start_node]
                            del latest_release_write[mem_loc]
                        if row['MO'] == 'release':
                            # if sequence is broken by another release, start a new sequence
                            latest_release_write[mem_loc] = node_id
                            ongoing_release_sequences[node_id] = [node_id]
                
            case 'atomic rmw':
                if mem_loc in latest_release_write:
                    start_node = latest_release_write[mem_loc]
                    ongoing_release_sequences[start_node].append(node_id)
                node_write.add(node_id)
                rf_relations.add((node_from, node_id))
            case _:
                pass
            
        hb_relations.update(sb_relations)
        hb_relations.update(sw_relations)
        # =============== Relations updated ============================
        match instr: 
            case 'atomic write':
                # Find write-write data races
                operations_before = data[data['#'] <= node_id]
                access_same_loc = operations_before[operations_before['Location'] == mem_loc]
                writes_same_loc = access_same_loc[(access_same_loc['Action type'] == 'atomic write') | (access_same_loc['Action type'] == 'atomic read')]
                exclude_self = writes_same_loc[writes_same_loc['#'] != node_id]
                for potential_race_id in exclude_self['#']:
                        if not path_exists(hb_relations, potential_race_id, node_id):
                            # print(f'DATA RACE: {potential_race_id} and {node_id} both access {mem_loc} without a HB relation')
                            # create_graph(data, rf_edges=rf_relations, hb_edges=hb_relations, swa_relation=sw_relations, draw_graph=True)
                            data_races.append((potential_race_id, node_id))
                            return data_races
            case 'atomic read':
                # TODO: I am unsure about this check
                node_from = int(row['RF'])
                if not (node_id not in not_ordered_memory_locations and \
                        node_from not in not_ordered_memory_locations) and \
                node_from in node_write and not path_exists(hb_relations, node_from, node_id):
                    # print(f"DATA RACE between nodes {node_from} and {node_id}")
                    # create_graph(data, rf_edges=rf_relations, hb_edges=hb_relations, swa_relation=sw_relations, draw_graph=False)
                    data_races.append((node_from, node_id))
                    return data_races
            case _: pass
        # create_graph(data, rf_edges=rf_relations, hb_edges=hb_relations, swa_relation=sw_relations, draw_graph=True)
    print("SWS:", sw_relations)
    print("HBS:", hb_relations)
    return data_races

if __name__ == "__main__":
    races = find_data_race('./races_traces/loops2.txt', draw_graph=True)
    print(f'Found races: {races}')
