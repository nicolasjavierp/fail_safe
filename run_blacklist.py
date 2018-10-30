#!/usr/local/bin/python3.6
# -*- coding: utf-8 -*-
from fail_safe import FailSafe
import os
import json
from time import sleep

THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
my_config_file = os.path.join(THIS_FOLDER, 'config.json')

#print(THIS_FOLDER)
#print(my_file)

with open(my_config_file, 'r') as f:
        config = json.load(f)

bungie_api_key = config['DEFAULT']['BUNGIE_API_KEY'] # 'secret-bungie-key-of-fail_safe'

#fs = FailSafe(api_key=os.environ["BUNGIE_API_KEY"]) # Never put your keys in code... export 'em!
fs = FailSafe(api_key=bungie_api_key)

#my_battle_tag="Javu#2632"
# Get Destiny MembershipId by pc gamertag
#my_destiny_id = fs.get_DestinyUserId(fs.format_PlayerBattleTag(my_battle_tag))
#print("Javu's Destiny ID is: {}".format(my_destiny_id)) 
# Get User's Profile info and more detailed Character info
#my_profile = fs.get_DestinyUserProfile(my_destiny_id, components=[100,200])
#print("This is Javu's Destiny profile: {}".format(my_profile))
# Get a random single game's post carnage stats
# game_stats = fs.get_postGameStats(100)
# print("Random Destiny 2 game's post carnage game stats: \n{}".format(game_stats))

# Get players clan
#my_destiny_clan_name = fs.get_PlayerClanName(my_destiny_id)
#print("Destiny player Javu is in: {}".format(my_destiny_clan_name))
#last_played = fs.get_PlayerLastLogin(my_destiny_id)
#print("Destiny player Javu last played: {}".format(last_played))
# fs.is_blacklisted(my_destiny_id)
# res = fs.get_ClanPlayerList(3111393)

fs.create_blacklist()

fs.clean_blacklist()

fs.print_blacklist_file()

print(fs.print_blacklist_basic())

#sendMail = False
#while not sendMail:
#    sendMail = fs.send_mail()
#    sleep(30)

exit(0)