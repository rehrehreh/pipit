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
game.local = 0
game.init()

@app.route('/')
def start():
    session['game'] = Game()
    return redirect(url_for('Play'))


@app.route('/play', methods = ['GET', 'POST'])
def Play():
    
    if 'game' in session:
        if request.method != 'POST':
            None
        elif request.form['guess'] == '...':
            session['game'].init()
        elif request.form['guess'] == 'give up':
            session['game'].give_up()
        else:
            # Guessing
            session['game'].check_guess(request.form['guess'].lower())     
        return render_template('index.html', game=session['game'])

    else:
        return redirect(url_for('start'))

    


@app.route('/about') 
def About(): 
    return render_template('about.html') 


if __name__ == "__main__":
    app.run()
