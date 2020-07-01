from riot_api import RiotApi

import pdb
import json
import sys
import traceback

CHAMPION_ID_FILENAME = 'champion_id.json'

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

def main():
  some_summ = Summoner(sys.argv[1])
  matches = RiotApi.get_matches_by_account(some_summ.get_account_id())
  print('Retrieved {} matches'.format(matches['endIndex'] - matches['startIndex']))

  match_num = 0
  for match in matches['matches']:
    match_num += 1
    try:
      match = Match(match['gameId'])
      match_raw = match.get_data()

      # Only matchmade Rift, bois
      if match_raw['gameMode'] != 'CLASSIC' or match_raw['gameType'] != 'MATCHED_GAME':
        print("{} is non-Rift or custom".format(match_num))
        continue

      # Find desired summoner among participants
      desired_id = 0
      for part_id in match_raw['participantIdentities']:
        if part_id['player']['accountId'] == some_summ.get_account_id():
          desired_id = part_id['participantId']
          break

      # Display champion and match stats
      for part in match_raw['participants']:
        if part['participantId'] == desired_id:
          champ_name = Champion.get_name(part['championId'])
          cs = (part['stats']['totalMinionsKilled'] +
              part['stats']['neutralMinionsKilled'])
          game_dur = match_raw['gameDuration']
          cs_per_min = cs/float(game_dur/60)
          print("{} : {}, {}cs / {}min {}s = {:0.2f}cs/min".format(
              match_num,
              champ_name,
              cs,
              game_dur//60,
              game_dur%60,
              cs_per_min))
          break
    except:
      extype, value, tb = sys.exc_info()
      traceback.print_exc()
      pdb.post_mortem(tb)

if __name__ == '__main__':
  main()
