# -*- coding: utf-8 -*-
"""
Created on Fri Sep 20 20:14:53 2024

@author: matth
"""
import random
import requests
from collections import Counter
import time
import os
import pickle
import datetime
import networkx as nx
import json

class Game():
    def __init__(self):
        self.cwd = os.getcwd()
        self.node_list = []
        self.start_up()
        self.config_startup()


        
        

    def start_up(self):
        # This function sets the paths of initial files
        self.word_file = os.path.join(self.cwd, 'new_words.pickle')
        self.paths_file = os.path.join(self.cwd, 'paths.pickle')
        self.config_file = os.path.join(self.cwd, 'config.json')

        with open(self.word_file, 'rb') as handle:
            self.words = pickle.load(handle)

        self.word_list = list(self.words.keys())
        self.word_length = len(self.word_list)
        return

#############################
    # Config Functions
#############################

    def config_startup(self):
        # This function will pull / save the daily config (paths, start, end)
        # IF the seed matches that in the config, it loads
        # IF it does not, it will set a new config
        
        self.config_dict = {}
        self.today =  datetime.date.today()
        self.seed = 10000*self.today.year + 100*self.today.month + self.today.day
        self.config_dict['seed'] = self.seed
        random.seed(self.seed) 

        if not self.check_config():
            self.start_num = int(random.random() * self.word_length)
            self.start = self.word_list[self.start_num]
            self.start_counter = Counter(self.start)
            self.make_graph()
            self.get_end()
            self.export_config()
        else:
            self.load_config()
        return

    def check_config(self):
        equivalent = 0
        try:
            with open(self.config_file, "r") as f:
                saved_config = json.load(f)
            equivalent = saved_config['seed'] == self.seed
            self.config_dict = saved_config
        except:
            print('No config loaded, generating config')
        return equivalent

    def make_graph(self):
        connection_file = os.path.join(self.cwd, 'connections.pickle')
        with open(connection_file, 'rb') as handle:
            self.connections = pickle.load(handle)
        self.G = nx.Graph()
        self.G.add_nodes_from(self.words.keys(), label = self.words.values())
        self.G.add_edges_from(self.connections)
        return

    def get_end(self):
        need_end = 1
        while need_end:
            self.end_num = int(random.random() * self.word_length)
            self.end = self.word_list[self.end_num]
            self.end_counter = Counter(self.end)
            self.starting_difference = 5 - sum((self.start_counter & self.end_counter).values())
            if self.starting_difference in [4, 5]:
                paths_exist = self.generate_paths()
                if paths_exist > 0:
                    need_end = 0
        return

    def generate_paths(self):
        self.start_node = self.words[self.start]['node']
        self.end_node = self.words[self.end]['node']
        self.shortest_path_path = nx.shortest_path(self.G, self.start_node, self.end_node)
        self.shortest_path = len(self.shortest_path_path)
        if type(self.shortest_path) == 0:
            return 0
        self.paths = list(nx.all_shortest_paths(self.G, self.start_node, self.end_node))
        with open(self.paths_file, 'wb') as handle:
            pickle.dump(self.paths, handle, protocol=pickle.HIGHEST_PROTOCOL)
        return len(self.paths)

    def load_config(self):
        with open(self.config_file, "r") as f:
            self.conf_dict = json.load(f)
        self.start = self.config_dict['start']
        self.end = self.config_dict['end']
        self.paths = self.config_dict['paths']

        self.shortest_path = len(self.paths[0])
        return

    def export_config(self):
        self.config_dict['start'] = self.start
        self.config_dict['end'] = self.end
        self.config_dict['paths'] = self.paths
        with open(self.config_file, "w") as f:
            json.dump(self.config_dict, f, indent=4)
        return


#############################
    # Init Functions
#############################

    def init(self):
        self.playing = 1
        self.current_word = self.start
        self.full_stack = []
        self.word_stack = []
        self.node_list = []
        self.invalid_guesses = []
        self.guesses = 0
        self.message = ''
        self.valid_guess = 1
        self.starting_stack()
        return

    def starting_stack(self):
        
        self.node_list.append(self.words[self.start]['node'])
        self.full_stack = []
        for i in range(0, self.shortest_path):
            d = {}
            if i == 0:
                # start
                d['word'] = self.start
                d['def'] = self.words[self.start]['definition']
                d['paths'] = len(self.paths)

            elif i == self.shortest_path -1:
                # end
                d['word'] = self.end
                d['def'] = self.words[self.end]['definition']
                d['paths'] = 1

            else:
                d['word'] = '...'
                d['paths'] = '??'
            self.full_stack.append(d)
        return

    def give_up(self):
        self.full_stack = []
        self.word_stack = []
        self.node_list = []
        for i, num in enumerate(self.paths[0]):
            word = [x for x in self.words.keys() if self.words[x]['node'] == num][0]
            self.node_list.append(num)
            self.current_node = self.words[word]['node']
            self.current_word_paths = [x for x in self.paths if x[0:len(self.node_list)] == self.node_list]
            self.full_stack.append({'word':word, 'paths': len(self.current_word_paths), 'def': self.words[word]['definition']})
        return
    
#############################
    # Checking guess
#############################

    def check_guess(self, guess):
        self.valid_guess = 1
        self.guess = guess
        self.guesses+=1

        # check if 5 letters
        self.check_is_5()

        # check if word
        if self.valid_guess:
            self.check_is_word()

        # Check if only chaning 1 letter
        if self.valid_guess:
            self.check_change()

        if self.valid_guess:
            self.check_end()
        return

    def check_is_5(self):
        self.is_5 = len(self.guess)==5
        if not self.is_5:
            self.invalid_guesses.append(self.guess)
            self.message = f'"{self.guess}" is not 5 letters, try again'
            self.valid_guess = 0
        return

    def check_is_word(self):
        self.is_word = self.guess in self.word_list
        if not self.is_word:
            self.invalid_guesses.append(self.guess)
            self.message = f'"{self.guess}" not found in dictionary, try again.'
            self.valid_guess = 0
        return

    def check_end(self):
        if self.end == self.guess:
            self.message='You win!'
            self.playing = 0
            self.full_stack[len(self.word_stack)]['word'] = self.current_word
            self.full_stack[len(self.word_stack)]['paths'] = len(self.current_word_paths)
        else:
            # it is a valid guess but is not done
            self.message = 'Valid input!'
            self.current_word = self.guess
            self.word_stack.append(self.guess)

            # Find how many paths remain
            self.current_node = self.words[self.current_word]['node']
            self.node_list.append(self.current_node)
            self.current_word_paths = [x for x in self.paths if x[0:len(self.node_list)] == self.node_list]

            self.full_stack[len(self.word_stack)]['word'] = self.current_word
            self.full_stack[len(self.word_stack)]['paths'] = len(self.current_word_paths)
            self.full_stack[len(self.word_stack)]['def'] = self.words[self.current_word]['definition']
        return

    def check_change(self):
        self.current_counter = Counter(self.current_word)
        self.guess_counter = Counter(self.guess)
        self.shared_letters = sum((self.current_counter & self.guess_counter).values())
        if self.shared_letters != 4:
            self.invalid_guesses.append(self.guess)
            self.message =f'"{self.guess}" does not change only a single letter, try again'
            self.valid_guess = 0
        return

