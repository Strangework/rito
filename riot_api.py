import functools
import json
import requests
import time

API_KEY_FILENAME = 'key'
CHAMPION_MASTERY_API = 'https://na1.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-summoner/{}?api_key={}'
MATCH_API = 'https://na1.api.riotgames.com/lol/match/v4/matches/{}?api_key={}'
MATCHES_BY_ACCOUNT_API = 'https://na1.api.riotgames.com/lol/match/v4/matchlists/by-account/{}?api_key={}'
SUMMONER_BY_NAME_API = 'https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{}?api_key={}'

class RiotApi:
  api_key_file = open(API_KEY_FILENAME)
  api_key = api_key_file.read()
  api_key_file.close()

  def api_retry(f):
    # Decorator which inspects API response and retries if invalid
    # Waits if rate limited
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
       while True:
         data = f(*args, **kwargs)
         if 'status' not in data:
           return data
         elif data['status']['status_code'] == 429:
           print('Rate limit exceeded - waiting for 5s')
           time.sleep(5)
         else:
           raise ValueError('API rejected request ({}) {}'.format(
               data['status']['status_code'], data['status']['message'])) 
    return wrapper

  @classmethod
  @api_retry
  def get_match(cls, match_id):
      resp = requests.get(
          MATCH_API.format(match_id, cls.api_key))
      return json.loads(resp.content)

  @classmethod
  @api_retry
  def get_summoner_by_name(cls, name):
    resp = requests.get(
        SUMMONER_BY_NAME_API.format(name, cls.api_key))
    return json.loads(resp.content)

  @classmethod
  @api_retry
  def get_matches_by_account(cls, account_id):
    resp = requests.get(
        MATCHES_BY_ACCOUNT_API.format(account_id, cls.api_key))
    return json.loads(resp.content)
