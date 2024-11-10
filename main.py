from flask import Flask, render_template, request, session
import collections
collections.MutableMapping = collections.abc.MutableMapping
collections.MutableSequence = collections.abc.MutableSequence
collections.Iterable = collections.abc.Iterable
from flask_navigation import Navigation 
from game import Game


# This is the variable that will be sent to the index.html
# and saved as a session
class state_intermediate:
    def __init__(self, game):
        self.valid_guess = 1
        self.message = ""
        self.full_stack = game.starting_stack()
        return

# initialize game object
game = Game()



# Flask startups
app = Flask(__name__)
app.secret_key = "meowmeowmeow"
nav = Navigation(app)
nav.Bar('top', [ 
    nav.Item('Play', 'Play'),
    nav.Item('About', 'About'), 
]) 


# Session will have:
# user, state_intermediate
@app.route('/', methods = ['GET', 'POST'])
def Play():
    
    if 'user' in session:
        if request.method != 'POST':
            None
        elif request.form['guess'] == '...':
            session.clear()
        elif request.form['guess'] == 'give up':
            session['state'].valid_guess, session['state'].message, session['state'].full_stack = game.give_up()
        else:
            # Guessing
            session['state'].valid_guess, session['state'].message, session['state'].full_stack = \
                game.check_guess(request.form['guess'], session['state']['full_stack'])

        return render_template('index.html', game=session['state'])

    else:
        session['user'] = request.remote_addr
        session['state'] = state_intermediate(game).__dict__
        return render_template('index.html', game=session['state'])

    


@app.route('/about') 
def About(): 
    return render_template('about.html') 


if __name__ == "__main__":
    app.run()
