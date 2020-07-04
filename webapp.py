import flask
app = flask.Flask(__name__)

from riot_api import RiotApi, Champion, Match, Summoner
import cs_per_min


@app.route('/')
def home():
  return flask.render_template('hello.html')

@app.route('/summoner/<summoner_name>')
def get_summoner_report(summoner_name):
  full_report = []
  if summoner_name != '':
    some_summ = Summoner(summoner_name)
    report = cs_per_min.generate_report(some_summ, 5)
    payload = {'report': report} 
  return flask.jsonify(payload)
