from flask import Flask, render_template, request, session, make_response, json
import collections
import traceback
collections.MutableMapping = collections.abc.MutableMapping
collections.MutableSequence = collections.abc.MutableSequence
collections.Iterable = collections.abc.Iterable
from flask_navigation import Navigation
from game import Game
from werkzeug.exceptions import InternalServerError
from datetime import timedelta

# initialize game object
game = Game()

# Flask startups
app = Flask(__name__)
app.secret_key = "meowmeowmeow"
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=10)
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

        else:
            for position in session['full_stack'].keys():
                data = request.form.get(f'guess{str(position)}')
                if data != None:
                    guess_word = data.replace(' ', '')
                    break

            # Guessing
            session['valid_guess'], session['message'], session['full_stack'] = \
                game.check_guess(guess_word, position, session['full_stack'])

    else:
        session.clear()
        session.permanent = False
        session['user'] = request.remote_addr
        session['full_stack'] = game.starting_stack()
        session['valid_guess'] = 4
        session['message'] = 'Awaiting a guess...'
        session['used_hint'] = 0


    # Set cookie Metric

    metric = request.cookies.get('metricCookie')
    if metric == None:
        #date num, #num wins
        metric = '01,0;02,0;03,0;04,0;05,0;06,0;07,0;08,0;09,0;10,0;11,0;12,0'

    # Set and compare seed for win
    seed = str(game.seed)
    seed_cookie = request.cookies.get('seedCookie')
    if seed_cookie == None:
        seed_cookie = 'none'

    if (seed_cookie != seed) and (session['valid_guess']==2):
        # Wooh, won! Update the seed_cookie and the metric
        metric = update_metric(metric, seed)
        seed_cookie = seed

    if (seed_cookie != seed) and (session['valid_guess']==3):
        # The user used a hint function, eliminate them from winning today
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
        score = int(mo_data[1])
        metric_dict[month]['score'] = score
        if score > 0:
            metric_dict[month]['class'] = 'score1'
        else:
            metric_dict[month]['class'] = 'score0'
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

@app.errorhandler(InternalServerError)
def handle_exception(e):
    """Return JSON instead of HTML for 500 errors."""
    # start with the correct headers and status code from the error
    response = e.get_response()
    tb = e.original_exception.__traceback__
    # replace the body with JSON
    response.data = json.dumps({
        "code": e.code,
        "name": e.name,
        "description": e.description,
        "stack": session['full_stack'],
        "metric": request.cookies.get('metricCookie'),
        "exception": traceback.format_tb(tb),
    })
    response.content_type = "application/json"
    return response

if __name__ == "__main__":
    app.run(debug=True)
