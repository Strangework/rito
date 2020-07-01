import flask
app = flask.Flask(__name__)

from riot_api import RiotApi, Champion, Match, Summoner
import cs_per_min


@app.route('/<summoner_name>')
def home(summoner_name):
  full_report = []
  if summoner_name != '':
    some_summ = Summoner(summoner_name)
    report = cs_per_min.generate_report(some_summ, 5)
  return flask.render_template('hello.html', report=report)
