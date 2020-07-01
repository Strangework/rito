import functools
import json
import requests
import time

API_KEY_FILENAME = 'key'
CHAMPION_ID_FILENAME = 'champion_id.json'

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
  def get_matches_by_account(cls, account_id, match_count):
    resp = requests.get(
        MATCHES_BY_ACCOUNT_API.format(account_id, cls.api_key),
        params={'endIndex': match_count})
    return json.loads(resp.content)


class Champion:
  # Load champion ID/name mapping
  champion_id_file = open(CHAMPION_ID_FILENAME)
  ID_NAME_MAP = json.loads(champion_id_file.read())
  champion_id_file.close()

  @classmethod
  def get_name(cls, champ_id):
    # champ ID is cast from int to str
    return cls.ID_NAME_MAP[str(champ_id)]

class Match:
  def __init__(self, match_id):
    self._data = RiotApi.get_match(match_id)

  def get_data(self):
    return self._data
    

class Summoner:
  def __init__(self, name):
    summ = RiotApi.get_summoner_by_name(name)
    self._name = summ['name']
    self._account_id = summ['accountId']
    self._summoner_id = summ['id']

  def get_account_id(self):
    return self._account_id

  def get_summoner_id(self):
    return self._summoner_id
