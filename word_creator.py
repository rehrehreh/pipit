# -*- coding: utf-8 -*-
"""
Created on Sun Sep 22 14:14:29 2024

@author: matth
"""

import enchant
import itertools
import time
import pandas as pd
import pickle
import os
from collections import Counter
import networkx as nx

from matplotlib import pyplot as plt

def generate_words(df, word_file):
    words = {}
    d = enchant.Dict("en_US") 
    for index, row in df.iterrows():
        if index % 10000 == 0:
            print(index)
        word = ''.join(row.to_list())
        if d.check(word):
            words[index] = word

    with open(word_file, 'wb') as handle:
        pickle.dump(words, handle, protocol=pickle.HIGHEST_PROTOCOL)

    return words


def generate_connections(prod, connection_file, equivalent_file):
    
    # create Counters
    prod['counter'] = ''
    for index, row in prod.iterrows():
        prod.loc[index, 'counter'] = [Counter(''.join(row.to_list()))]
        
    connections = []
    equivalents = []
    # check shared letters
    for index_i, row_i in prod.iterrows():
        shared = []
        for index_ii, row_ii in prod.iterrows():
            connection = (index_i, index_ii)
            shared_letters = sum((row_i['counter'][0] & row_ii['counter'][0]).values())
            if shared_letters == 4:
                connections.append(connection)
            if shared_letters == 5:
                equivalents.append(connection)
                
        
    with open(connection_file, 'wb') as handle:
        pickle.dump(connection, handle, protocol=pickle.HIGHEST_PROTOCOL)
    with open(equivalent_file, 'wb') as handle:
        pickle.dump(equivalents, handle, protocol=pickle.HIGHEST_PROTOCOL)
    return connections, equivalents



cwd = os.getcwd()
start_time = time.perf_counter()


cols = ['i', 'ii', 'iii', 'iv', 'v']

alphabet = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 
            'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
nums = list(range(1,27))

possibilities = itertools.product(alphabet, alphabet, alphabet, alphabet, alphabet)
df = pd.DataFrame(possibilities, columns = cols)

word_file = os.path.join(cwd, 'words.pickle')
connection_file = os.path.join(cwd, 'connections.pickle')
equivalent_file = os.path.join(cwd, 'equivalent.pickle')
graph_file = os.path.join(cwd, 'graph.pickle')
gen_words = 0

if gen_words:
    words = generate_words(df, word_file)
else:
    with open(word_file, 'rb') as handle:
        words = pickle.load(handle)

prod = df.loc[words.keys(),:]

gen_conns = 0
if gen_conns:
    connections, equivalents = generate_connections(prod, connection_file, equivalent_file)
else:
    with open(connection_file, 'rb') as handle:
        connections = pickle.load(handle)
    with open(equivalent_file, 'rb') as handle:
        equivalents = pickle.load(handle)

### Graph
G = nx.Graph()
G.add_nodes_from(words.keys(), label = words.values())
G.add_edges_from(connections)

# with open(graph_file, 'wb') as handle:
#     pickle.dump(G, handle, protocol=pickle.HIGHEST_PROTOCOL)
# islands = {}
# for i, c in enumerate(nx.connected_components(G)):
#     l = []
#     if len(c)<5:
#         for x in c:
#             l.append(words[x])
#     islands[i] = l

start = [x for x in words.keys() if words[x] == 'cobra'][0]
end = [x for x in words.keys() if words[x] == 'quiff'][0]
#start = [n for n in G.nodes(data=True) if n['label'] == 'pylon']
paths = list(nx.all_shortest_paths(G, start, end))
print(len(paths))

# nx.draw(G)
# plt.show()


end_time = time.perf_counter()
elapse = round(end_time - start_time, 2)
print(f'Time Elapsed (s): {elapse}')