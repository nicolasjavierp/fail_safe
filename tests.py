#!/usr/local/bin/python3.6
# -*- coding: utf-8 -*-
from fail_safe import FailSafe
import os
from urllib.request import urlopen
import json
import random
import pymongo
from pymongo import MongoClient
from datetime import datetime
import time
import tweepy


THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
my_config_file = os.path.join(THIS_FOLDER, 'config.json')

fs = FailSafe(api_key=os.environ["BUNGIE_API_KEY"]) # Never put your keys in code... export 'em!
#print(fs.get_PlayerClanName("4611686018472677917"))

with open(my_config_file, 'r') as f:
            config = json.load(f)

MONGODB_URI = config['DEFAULT']['MONGO_DB_MLAB']
client = MongoClient(MONGODB_URI, connectTimeoutMS=30000)
db = client.get_database("bot_definitivo")
clanmates = db.clan_members
blacklisters = db.blacklist
discord_users = db.discord_users

TWITTER_ACCESS_SECRET='OrTWgB5Bt4bOjZXPkR6BeByObrqh91azBTy4ebmgZOToB'
TWITTER_ACCESS_TOKEN='279556940-PlRMbi9byLOw9dVBGDEKh5znlUh38Bbu7eQKOrAz'
TWITTER_API_KEY='20rgToegag5drInpyJwsiPvN6'
TWITTER_API_SECRET='B4gvUPr9KHKHdnD9btgdLlkRH8yFjhpyewSS7EJECXDOCnzjbX'


auth=tweepy.OAuthHandler(TWITTER_API_KEY,TWITTER_API_SECRET)
auth.set_access_token(TWITTER_ACCESS_TOKEN,TWITTER_ACCESS_SECRET)
api = tweepy.API(auth)
tweets = api.user_timeline("BungieHelp",page=1)
for tweet in tweets:
        if "maintenance has begun" in tweet.text:
                print(tweet.text)
        #await client.send_message(context.message.channel, tweet)





def get_one_Clanmate(clanmate_id):
        document = clanmates.find_one({'battletag':clanmate_id})
        return document


def get_all_Discord_Users_by_last_activity():
        document = discord_users.find({}).sort('last_activity',pymongo.DESCENDING)
        return document


def get_one_Discord_User(discord_id):
        document = discord_users.find_one({'discord_id':discord_id})
        return document


def is_Clanmate_in_db(clanmate_id):
        document = clanmates.find_one({'battletag':clanmate_id})
        if document:
                return True
        else:
                return False

def is_Discord_User_in_db(discord_id):
        document = discord_users.find_one({'discord_id':discord_id})
        if document:
                return True
        else:
                return False


def update_Discord_User(record, updates):
        discord_users.update_one({'_id': record['_id']},{
                                '$set': updates
                                }, upsert=False)







print("Done!")

#db.posts.find(...).sort([
#  ('date', pymongo.ASCENDING),
#  ('other_field', pymongo.DESCENDING)
#]):

#fs.print_blacklist_file()
#fs.clean_clan_file()
#fs.create_blacklist()
#fs.clean_blacklist()
#fs.print_blacklist_file()



#"Javu#2632": [
#        "Escuadra 4",
#        "Javu"
#    ],

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