from flask import Flask, render_template, request, session, redirect, url_for 
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
app.secret_key = "meowmeowmeow"
nav = Navigation(app)
nav.Bar('top', [ 
    nav.Item('Play', 'Play'),
    nav.Item('About', 'About'), 
]) 


game = Game()
game.init()


@app.route('/', methods = ['GET', 'POST'])
def Play():
    
    if 'user' in session:
        if request.method != 'POST':
            None
        elif request.form['guess'] == '...':
            game.init()
        elif request.form['guess'] == 'give up':
            game.give_up()
            session.pop('user')
        else:
            # Guessing
            game.check_guess(request.form['guess'].lower())
            if game.playing == 0:
                session.pop('user')
        return render_template('index.html', game=game)

    else:
        session['user'] = request.remote_addr
        return render_template('index.html', game=game)

    


@app.route('/about') 
def About(): 
    return render_template('about.html') 


if __name__ == "__main__":
    app.run()
