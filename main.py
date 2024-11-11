from flask import Flask, render_template, request, session
import collections
collections.MutableMapping = collections.abc.MutableMapping
collections.MutableSequence = collections.abc.MutableSequence
collections.Iterable = collections.abc.Iterable
from flask_navigation import Navigation 
from game import Game


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
            game = Game()
            session['user'] = request.remote_addr
            session['full_stack'] = game.starting_stack()
            session['valid_guess'] = 1
            session['message'] = ''

        elif request.form['guess'].lower() == 'give up':
            session['valid_guess'], session['message'], session['full_stack'] = game.give_up()

        else:
            # Guessing
            session['valid_guess'], session['message'], session['full_stack'] = \
                game.check_guess(request.form['guess'].lower(), session['full_stack'])

        return render_template('index.html', full_stack=session['full_stack'], valid_guess = session['valid_guess'], message = session['message'])

    else:
        game = Game()
        session['user'] = request.remote_addr
        session['full_stack'] = game.starting_stack()
        session['valid_guess'] = 1
        session['message'] = ''
        return render_template('index.html', full_stack=session['full_stack'], valid_guess = session['valid_guess'], message = session['message'])

    


@app.route('/about') 
def About(): 
    return render_template('about.html') 


if __name__ == "__main__":
    app.run()
