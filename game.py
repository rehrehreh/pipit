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
from zoneinfo import ZoneInfo

class Game():
    def __init__(self):
        self.cwd = os.getcwd()
        self.start_up()
        self.config_startup()
        self.valid_message = 'Valid Input!'
        
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
        self.today =  datetime.datetime.now(tz=ZoneInfo("America/New_York"))
        self.seed = 10000*self.today.year + 100*self.today.month + self.today.day
        self.config_dict['seed'] = self.seed
        random.seed(self.seed) 

        if not self.check_config():
            self.start_num = int(random.random() * (self.word_length-1))
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
            self.end_num = int(random.random() * (self.word_length-1))
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
    # Functions with main
#############################

    def starting_stack(self):
        self.start_up()
        self.config_startup()
        full_stack = {}
        for i in range(0, self.shortest_path):
            if i == 0:
                # start
                full_stack[i] = {}
                full_stack[i]['word'] = self.start
                full_stack[i]['def'] = self.words[self.start]['definition']
                full_stack[i]['paths'] = len(self.paths)

            elif i == self.shortest_path -1:
                # end
                n = 99
                full_stack[n] = {}
                full_stack[n]['word'] = self.end
                full_stack[n]['def'] = self.words[self.end]['definition']
                full_stack[n]['paths'] = 1

            else:
                full_stack[i] = {}
                full_stack[i]['word'] = '...'
                full_stack[i]['def'] = ''
                full_stack[i]['paths'] = '??'

        return full_stack

    def give_up(self, full_stack):
        random.seed(time.time() * 1000)
        # Node list for determining current paths
        node_list = []
        for key in full_stack.keys():
            if full_stack[key]['word'] == '...' or int(key) == 99:
                continue
            word = full_stack[key]['word']
            node_list.append(self.words[word]['node'])
        
        # check if there are any possible paths given the current stack
        current_word_paths = [x for x in self.paths if x[0:len(node_list)] == node_list]
        if len(current_word_paths)>0:
            use_num = int(random.random() * (len(current_word_paths)-1))
            use_path = current_word_paths[use_num]

        else:
            # use a random path because the current set cannot be filled in
            use_num = int(random.random() * (len(self.paths)-1))
            use_path = self.paths[use_num]

        # Returns valid guess, message, full_stack
        full_stack = {}
        node_list = []
        for i, num in enumerate(use_path):
            word = [x for x in self.words.keys() if self.words[x]['node'] == num][0]
            node_list.append(num)
            current_word_paths = [x for x in self.paths if x[0:len(node_list)] == node_list]
            definition = self.words[word]['definition']

            full_stack[i] = {}
            full_stack[i]['word'] = word
            full_stack[i]['def'] = definition
            full_stack[i]['paths'] = len(current_word_paths)
        return 3, 'This is one possible shortest path', full_stack
    
#############################
    # Checking guess
#############################

    def check_guess(self, guess, position, full_stack):
        # Returns valid guess, message, full_stack

        # check if ...
        reset, full_stack = self.check_dotdotdot(guess, full_stack)
        if reset:
            valid_guess = 1
            message = 'Word reset'
            return valid_guess, message, full_stack 

        # check if 5 letters
        valid_guess, message = self.check_is_5(guess)

        # check if word
        if valid_guess:
            valid_guess, message = self.check_is_word(guess)

        # Update Stack
        if valid_guess:
            full_stack = self.update_stack(guess, position, full_stack)
            win = self.check_end(full_stack)
            if win:
                valid_guess = 2
                message = 'You won!'

        return valid_guess, message, full_stack


    def check_dotdotdot(guess, position, full_stack):
        if guess == '...':
            reset = True
            full_stack[position] = {}
            full_stack[position]['word'] = guess
            full_stack[position]['paths'] = '??'
            full_stack = dict(sorted(full_stack.items()))

        else: 
            reset = False
        return reset, full_stack

    def check_is_5(self, guess):
        valid_guess = 1
        message = self.valid_message
        is_5 = len(guess)==5
        if not is_5:
            message = f'"{guess}" is not 5 letters, try again'
            valid_guess = 0
        return valid_guess, message

    def check_is_word(self, guess):
        valid_guess = 1
        message = self.valid_message
        is_word = guess in self.word_list
        if not is_word:
            message = f'"{guess}" not found in dictionary, try again.'
            valid_guess = 0
        return valid_guess, message

#####################################
# Extracting the last word from full starting_stack
########################################
    
    def latest_word(self, full_stack):
        temp = []
        for key in full_stack.keys():
            if int(key) == 99:
                continue
            
            if full_stack[key]['word'] == '...':
                continue
            else:
                temp.append(int(key))
        
        return max(temp)
    
    def update_stack(self, guess, position, full_stack):
        full_stack[position] = {}
        full_stack[position]['word'] = guess
        full_stack[position]['def'] = self.words[guess]['definition']
        possible_paths = self.find_paths(full_stack, position)
        full_stack[position]['paths'] = len(possible_paths)
        full_stack = dict(sorted(full_stack.items()))
        return full_stack


    def find_paths(self, full_stack):
        node_list = []
        node_keys =[]
        for key in full_stack.keys():
            if full_stack[key]['word'] == '...' or int(key) == 99:
                continue
            word = full_stack[key]['word']
            node_list.append(self.words[word]['node'])
            node_keys.append(int(key))

        possible_paths = [x for x in self.paths if x[node_keys] == node_list]
        return possible_paths
    
    def check_end(self, full_stack):
        for key in full_stack.keys():
            if full_stack[key]['word'] == '...' or full_stack[key]['paths'] == 0:
                # not done
                return 0
            else:
                continue
        return 1
            
