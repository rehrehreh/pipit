# -*- coding: utf-8 -*-
"""
Created on Fri Sep 20 20:14:53 2024

@author: matth
"""
import enchant
import random
import requests
from collections import Counter
import time
import os
import pickle
import datetime

class Game():
    def __init__(self):
        self.dict = enchant.Dict("en_US") 
        self.cwd = os.getcwd()
        # Get words
        self.word_file = os.path.join(self.cwd, 'words.pickle')
        with open(self.word_file, 'rb') as handle:
            self.words = pickle.load(handle)
        self.word_list = list(self.words.values())
        self.word_length = len(self.word_list)

        # seed = 44
        today =  datetime.date.today()
        self.seed = 10000*today.year + 100*today.month + today.day
        random.seed(self.seed)
        self.start_num = int(random.random() * self.word_length)
        self.start = self.word_list[self.start_num]
        self.start_counter = Counter(self.start)

        self.get_end()

        # Set init values


        self.local = 1


    def gen_full(self):
        self.full_stack = []
        self.full_stack.append(self.start)
        self.full_stack.extend(self.word_stack)
        if self.playing:
            self.full_stack.append('.....')
        self.full_stack.append(self.end)

        # gen color code
        self.color_stack = []
        for word in self.full_stack:
            colors = []
            for letter in word:
                if letter in self.end:
                    color = 2
                else:
                    color = 0
                colors.append(color)
            self.color_stack.append(colors)
        return

    def init(self):
        self.start_time = time.perf_counter()
        self.playing = 1
        self.current_word = self.start
        self.word_stack = []
        self.invalid_guesses = []
        self.guesses = 0
        self.message = ''
        self.valid_guess = 1
        self.gen_full()
        self.word_score = False
        self.invalid_penalty = False
        self.time_score = False
        self.score = False
        return

    def get_end(self):
        need_end = 1
        while need_end:
            end_num = int(random.random() * self.word_length)
            end = self.word_list[end_num]
            end_counter = Counter(end)
            shared_letters = sum((self.start_counter & end_counter).values())
            if shared_letters in [0, 1]:
                need_end = 0
        self.starting_difference = 5- shared_letters
        self.end_counter = end_counter
        self.end = end
        return

    def get_score(self):
        self.word_score = round(1-(len(self.word_stack) - self.starting_difference)/8, 3)
        self.invalid_penalty = -0.07 * len(self.invalid_guesses)
        self.time_score = round(1 - (self.total_time)/600, 3)
        self.score = round(self.word_score + self.invalid_penalty + self.time_score, 3)
        return


    def print_metrics(self):
        if self.local:
            print('-----------------------------------------')
            print(self.message)
            print(f'Words between: {len(self.word_stack)}')
            print(f'Invalid inputs: {len(self.invalid_guesses)}')
            print(f'Total tries: {self.guesses}\n')
            if not self.playing:
                print(f'Total Time: {self.total_time}')
                print(f'Total Score: {self.score}')
                print(f'Word Score: {self.word_score}')
                print(f'Timing Score: {self.time_score}')
                print(f'Invalid Penalties: {self.invalid_penalty}')
        return

    def print_stack(self):
        if self.local:
            print('Word stack:')
            print(self.start)
            for x in self.word_stack:
                print(x)
            if self.playing:
                print('...')
            print(self.end)
        return

    def check_is_5(self):
        self.is_5 = len(self.guess)==5
        if not self.is_5:
            self.invalid_guesses.append(self.guess)
            self.message = f'"{self.guess}" is not 5 letters, try again'
            self.valid_guess = 0
        return


    def check_is_word(self):
        self.is_word = self.dict.check(self.guess)
        if not self.is_word:
            self.invalid_guesses.append(self.guess)
            self.message = f'"{self.guess}" not found in dictionary, try again.'
            self.valid_guess = 0
        return

    def check_end(self):
        if self.end == self.guess:
            self.message='You win!'
            self.playing = 0
            self.gen_full()
            self.end_time = time.perf_counter()
            self.total_time = round(self.end_time - self.start_time, 1)
        else:
            # it is a valid guess but is not done
            self.message = 'Valid input!'
            self.current_word = self.guess
            self.word_stack.append(self.guess)
            self.gen_full()
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

    def play_local(self):
        
        self.init()
        while self.playing:  
            self.valid_guess = 1
            self.print_metrics()
            self.print_stack()
            


            self.guess = input('Next Word: ')
            print(self.guess)
            self.guesses+=1

            # check if word
            self.check_is_word()
            if not self.valid_guess:
                continue
            
            # Check if only chaning 1 letter
            self.check_change()
            if not self.valid_guess:
                continue
            
            # Check if equal to end
            self.check_end()
            if self.playing == 0:
                self.get_score()
                self.print_metrics()
                self.print_stack()
        return



if __name__ == "__main__":
    game = Game()
    game.play_local()