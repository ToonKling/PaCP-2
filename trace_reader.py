import numpy as np
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

with open('./trace.txt') as f:
    lines = f.readlines()
    data = pd.DataFrame()
    data['#'] = [line[0:5].strip() for line in lines]
    data['thread'] = [line[5:9].strip() for line in lines]
    data['Action type'] = [line[10:26].strip() for line in lines]
    data['MO'] = [line[26:35].strip() for line in lines]
    data['Location'] = [line[35:54].strip() for line in lines]
    data['Value'] = [line[54:74].strip() for line in lines]
    data['RF'] = [line[74:78].strip() for line in lines]
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

