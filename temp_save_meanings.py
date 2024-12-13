# -*- coding: utf-8 -*-
"""
Created on Sun Nov  3 16:31:17 2024

@author: HelloWorld
"""

import enchant
import random
import requests
from collections import Counter
import time
import os
import pickle
import datetime
import networkx as nx
import json

from PyDictionary import PyDictionary

class Game():
    def __init__(self):
        self.dict = enchant.Dict("en_US") 
        self.cwd = os.getcwd()
        self.dictionary = PyDictionary()
        self.node_list = []
        # Get words
        self.word_file = os.path.join(self.cwd, 'words.pickle')
        self.new_file = os.path.join(self.cwd, 'new_words.pickle')
        with open(self.word_file, 'rb') as handle:
            self.words = pickle.load(handle)
        
game = Game()

new_words = {}
for key in game.words.keys():
    word = game.words[key]
    definition = game.dictionary.meaning(word, disable_errors=True)
    new_words[word] = {}
    new_words[word]['node']=key
    new_words[word]['definition']=definition

with open(game.new_file, 'wb') as handle:
        pickle.dump(new_words, handle, protocol=pickle.HIGHEST_PROTOCOL)