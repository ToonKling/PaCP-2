import numpy as np
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import regex as re

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
                    'thread':match.group(2),
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
print(f'df: \n{data}')

G = nx.DiGraph()

for instr in data['#']:
    G.add_node(instr)

edge_labels = {}

# Operation order edges
op_rels = data.groupby('thread')['#'].apply(list)
for ops in op_rels:
    for op in range(len(ops)-1):
        print(f'OP: {ops[op]} to {ops[op+1]}')
        G.add_edge(ops[op], ops[op+1])
        edge_labels[(ops[op], ops[op+1])] = 'op'

# RF edges
for i in range(len(data)):
    if data['RF'][i] != '':
        print(f'RF: {data['RF'][i]} from {data['#'][i]}')
        G.add_edge(data['#'][i], data['RF'][i])
        edge_labels[data['#'][i], data['RF'][i]] = 'rf'

# Thread spawning edges, not sure if correct :o
for i in range(len(data)):
    if data['Action type'][i] == 'thread create':
        for j in range(i, len(data)):
            if data['Action type'][j] == 'thread start':
                f = data['#'][i]
                t = data['#'][j]
                print(f'Thread spawn: {f} to {t}')
                G.add_edge(f, t)
                edge_labels[f, t] = 'asw'
                break

# Giant mess with the types, oops
pos = {str(i+1): [int(data['#'][i]), int(data['thread'][i])] for i in range(len(data))}
print(f'pos: {pos}')
nx.draw_networkx(G, pos)
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
plt.show()

