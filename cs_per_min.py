from riot_api import RiotApi, Champion, Match, Summoner

import pdb
import sys
import traceback

def generate_report(some_summ, match_count):
  matches = RiotApi.get_matches_by_account(some_summ.get_account_id(), match_count)
  print('Retrieved {} matches'.format(matches['endIndex'] - matches['startIndex']))

  full_report = []

  match_num = 0
  for match in matches['matches']:
    match_num += 1
    match = Match(match['gameId'])
    match_raw = match.get_data()

    # Only matchmade Rift, bois
    if match_raw['gameMode'] != 'CLASSIC' or match_raw['gameType'] != 'MATCHED_GAME':
      match_report = "{} is non-Rift or custom".format(match_num)
      print(match_report)
      full_report.append(match_report)
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
        report = "{} : {}, {}cs / {}min {}s = {:0.2f}cs/min".format(
            match_num,
            champ_name,
            cs,
            game_dur//60,
            game_dur%60,
            cs_per_min)
        full_report.append(report)
        print(report)
        break
  return full_report

if __name__ == '__main__':
  try:
    some_summ = Summoner(sys.argv[1], int(sys.argv[2]))
    generate_report(some_summ)
  except:
    extype, value, tb = sys.exc_info()
    traceback.print_exc()
    pdb.post_mortem(tb)

