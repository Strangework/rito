import pdb
import json
import requests
import traceback
import sys

CHAMPION_ID_FILENAME = 'champion_id.json'

# !! Load in API key in a neater way...
API_KEY = ''
CHAMPION_MASTERY_API = 'https://na1.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-summoner/{}?api_key={}'
MATCH_API = 'https://na1.api.riotgames.com/lol/match/v4/matches/{}?api_key={}'
MATCH_BY_ACCOUNT_API = 'https://na1.api.riotgames.com/lol/match/v4/matchlists/by-account/{}?api_key={}'
SUMMONER_BY_NAME_API = 'https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{}?api_key={}'

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
    resp = requests.get(
        MATCH_API.format(match_id, API_KEY))
    # !! Handle bad status codes wherever APIs are called
    self._data = json.loads(resp.content)

  def get_data(self):
    return self._data
    

class Summoner:
  def __init__(self, name):
    resp = requests.get(
        SUMMONER_BY_NAME_API.format(name, API_KEY))
    resp = json.loads(resp.content)
    self._name = resp['name']
    self._account_id = resp['accountId']
    self._summoner_id = resp['id']

  def get_account_id(self):
    return self._account_id

  def get_summoner_id(self):
    return self._summoner_id

def main():
  vyle = Summoner("Vylemaw")
  resp = requests.get(
      MATCH_BY_ACCOUNT_API.format(vyle.get_account_id(), API_KEY))
  resp = json.loads(resp.content)
  matches = resp['matches']

  for match in matches:
    match = Match(match['gameId'])
    match_raw = match.get_data()

    try:
      # Only matchmade Rift, bois
      if match_raw['gameMode'] != 'CLASSIC' or match_raw['gameType'] != 'MATCHED_GAME':
        continue
    except:
      extype, value, tb = sys.exc_info()
      traceback.print_exc()
      pdb.post_mortem(tb)

    desired_id = 0
    for part_id in match_raw['participantIdentities']:
      if part_id['player']['accountId'] == vyle.get_account_id():
        desired_id = part_id['participantId']
        break
    for summ in match_raw['participants']:
      if summ['participantId'] == desired_id:
        champ_name = Champion.get_name(summ['championId'])
        cs = (summ['stats']['totalMinionsKilled'] +
            summ['stats']['neutralMinionsKilled'])
        game_dur = match_raw['gameDuration']
        cs_per_min = cs/float(game_dur/60)
        print("{} : {}cs / {}min {}s = {:0.2f}cs/min".format(
            champ_name,
            cs,
            game_dur//60,
            game_dur%60,
            cs_per_min))
        break

if __name__ == '__main__':
  main()
