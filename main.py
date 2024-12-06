from flask import Flask, render_template, request, session, make_response
import collections
collections.MutableMapping = collections.abc.MutableMapping
collections.MutableSequence = collections.abc.MutableSequence
collections.Iterable = collections.abc.Iterable
from flask_navigation import Navigation 
from game import Game
from datetime import timedelta

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
            session['full_stack'] = game.starting_stack()
            session['valid_guess'] = 4
            session['message'] = ''

        elif request.form['guess'].lower() == 'give up':
            session['valid_guess'], session['message'], session['full_stack'] = game.give_up(full_stack = session['full_stack'])

        else:
            # Guessing
            session['valid_guess'], session['message'], session['full_stack'] = \
                game.check_guess(request.form['guess'].lower(), session['full_stack'])

    else:
        session.permanent = True
        session['user'] = request.remote_addr
        session['full_stack'] = game.starting_stack()
        session['valid_guess'] = 4
        session['message'] = ''


    # Set cookie
    metric = request.cookies.get('metricCookie')
    print(metric)
    if metric == None:
        metric = '444444444444444444444'

    # Update metric with last guess
    metric = str(session['valid_guess']) + metric[0:-1] 
    print(metric)
    resp = make_response(render_template('index.html', full_stack=session['full_stack'],
                                            valid_guess = session['valid_guess'],
                                            message = session['message'],
                                            metric = metric)) 
    resp.set_cookie('metricCookie', metric) 
    return resp

    


@app.route('/about') 
def About(): 
    return render_template('about.html') 


if __name__ == "__main__":
    app.run()
