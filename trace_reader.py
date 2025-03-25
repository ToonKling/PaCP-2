
import regex as re
import pandas as pd

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


data = read_from_file('./trace.txt')
#
# for instr in data['#']:
#     G.add_node(instr)
#
# edge_labels = {}
#
# # Operation order edges
# op_rels = data.groupby('thread')['#'].apply(list)
# for ops in op_rels:
#     for op in range(len(ops)-1):
#         print(f'OP: {ops[op]} to {ops[op+1]}')
#         G.add_edge(ops[op], ops[op+1])
#         edge_labels[(ops[op], ops[op+1])] = 'op'
#
# # RF edges
# for i in range(len(data)):
#     if data['RF'][i] != '':
#         print(f'RF: {data['RF'][i]} from {data['#'][i]}')
#         G.add_edge(data['#'][i], data['RF'][i])
#         edge_labels[data['#'][i], data['RF'][i]] = 'rf'
#
# # Thread spawning edges, not sure if correct :o
# for i in range(len(data)):
#     if data['Action type'][i] == 'thread create':
#         for j in range(i, len(data)):
#             if data['Action type'][j] == 'thread start':
#                 f = data['#'][i]
#                 t = data['#'][j]
#                 print(f'Thread spawn: {f} to {t}')
#                 G.add_edge(f, t)
#                 edge_labels[f, t] = 'asw'
#                 break
#

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
    if mem_loc_node.__contains__(mem_loc):
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
    if last_seen_thread.__contains__(thread_number):
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
            if not not_ordered_memory_locations.__contains__(node_id) and \
                    not not_ordered_memory_locations.__contains__(node_to):
                hb_edges.append((node_to, node_id))
            elif node_write.__contains__(node_to): # I think this already meets conditions for a data race.
                print(f"DATA RACE between nodes {node_to} and {node_id}")
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

