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


    # Set cookie Metric

    metric = request.cookies.get('metricCookie')
    if metric == None:
        #date num, #num wins
        metric = '01,0;02,0;03,0;04,0;05,0;06,0;07,0;08,0;09,0;10,0;11,0;12,0'

    # Set and compare seed for win
    seed = str(game.seed)
    seed_cookie = request.cookies.get('seedCookie')
    if (seed_cookie == None or seed_cookie != seed) and (session['valid_guess']==2):
        # Wooh, won! Update the seed_cookie and the metric
        print('updating metric')
        metric = update_metric(metric, seed)
        seed_cookie = seed

    metric_dict = metric_passthrough(metric)
    resp = make_response(render_template('index.html', full_stack=session['full_stack'],
                                            valid_guess = session['valid_guess'],
                                            message = session['message'],
                                            metric = metric_dict)) 
    resp.set_cookie('metricCookie', metric) 
    resp.set_cookie('seedCookie', seed_cookie) 
    return resp

def metric_passthrough(metric):
    metric_dict = {}
    metric_mos = metric.split(';')
    letters = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    for mo in metric_mos:
        mo_data = mo.split(',')
        month = str(mo_data[0])
        metric_dict[month] = {} 
        metric_dict[month]['score'] = int(mo_data[1])
        metric_dict[month]['letter'] = str(letters[int(mo_data[0])-1])
    return metric_dict

def update_metric(metric, seed):
    month = seed[4:6]
    metric_mos = metric.split(';')
    new_mos = []
    for mo in metric_mos:
        mo_data = mo.split(',')
        if mo_data[0] == month:
            mo_data[1] = str(int(mo_data[1])+1) 
            print('updated')
        mo_string = ','.join(mo_data)
        new_mos.append(mo_string)
    new_metric = ';'.join(new_mos)
    return new_metric

@app.route('/about') 
def About(): 
    return render_template('about.html') 


if __name__ == "__main__":
    app.run()
