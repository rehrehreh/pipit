from flask import Flask, render_template, request
import collections
collections.MutableMapping = collections.abc.MutableMapping
collections.MutableSequence = collections.abc.MutableSequence
collections.Iterable = collections.abc.Iterable
from flask_navigation import Navigation 
from game import Game

class Test:
    def __init__(self):
        self.message = 'Hello'
        self.user_input = False


app = Flask(__name__)
nav = Navigation(app)
nav.Bar('top', [ 
    nav.Item('Play', 'Play'),
    nav.Item('About', 'About'), 
]) 


game = Game()
game.local = 0
game.init()


@app.route('/', methods = ['GET', 'POST'])
def Play():

    if request.method != 'POST':
        game.init()
    elif request.form['guess'] == '...':
        game.init()
    elif request.form['guess'] == 'give up':
        game.give_up()
    else:

        game.valid_guess = 1
        game.guess = request.form['guess'].lower()
        game.guesses+=1


        # check if 5 letters
        game.check_is_5()

        # check if word
        if game.valid_guess:
            game.check_is_word()

        # Check if only chaning 1 letter
        if game.valid_guess:
            game.check_change()

                
        if game.valid_guess:
            game.check_end()
            if game.playing == 0:
                game.get_score()


            # Process the user input here (e.g., store it in a database, perform calculations)
    return render_template('index.html', game=game)


@app.route('/about') 
def About(): 
    return render_template('about.html') 


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
