# -*- coding: utf-8 -*-
# Works with Python 3.6

import asyncio
from pymongo import MongoClient


#//////////////////////////////////////////////////////////////////////
#////////////////   DB SECTION           //////////////////////////////
#//////////////////////////////////////////////////////////////////////
#https://mlab.com/databases/bot_definitivo/collections


######
#Blacklist
######
async def get_blacklist(blacklisters):
    document = blacklisters.find({})
    await asyncio.sleep(0.01)
    if document:
        return document
    else:
        return None


async def get_blacklist_date(blacklisters):
    document = blacklisters.find_one()
    await asyncio.sleep(0.01)
    if document:
        return str(document["date"])
    else:
        return None


######
#Clanmates
######
async def push_clanmate_to_db(record, clanmates):
    clanmates.insert_one(record)
    await asyncio.sleep(0.01)


def get_one_Clanmate(clanmate_id, clanmates):
    document = clanmates.find_one({'battletag':clanmate_id})
    if document:
        return document
    else:
        return None


def is_clanmate_in_db(clanmate_id, clanmates):
    document = clanmates.find_one({'battletag':clanmate_id})
    if document:
        return True
    else:
        return False


######
#Discord
######
async def push_discord_user_db(record, discord_users):
    discord_users.insert_one(record)
    await asyncio.sleep(0.01)


def get_all_discord_users_by_last_activity(discord_users):
    document = discord_users.find({}).sort('last_activity',pymongo.DESCENDING)
    #await asyncio.sleep(0.01)
    return document


def get_one_discord_user(discord_id, discord_users):
    document = discord_users.find_one({'discord_id':discord_id})
    return document


def is_discord_id_in_db(discord_id, discord_users):
    document = discord_users.find_one({'discord_id':discord_id})
    if document:
            return True
    else:
            return False


def update_discord_user(record, updates, discord_users):
    discord_users.update_one({'_id': record['_id']},{
                            '$set': updates
                            }, upsert=False)


async def async_add_discord_users_list(discord_users_list):
    #4 tests
    #MONGODB_URI = load_param_from_config('MONGO_DB_MLAB')
    #4 Heroku
    MONGODB_URI = os.environ['MONGO_DB_MLAB']
    #END Heroku
    cursor = MongoClient(MONGODB_URI, connectTimeoutMS=30000)
    db = cursor.get_database("bot_definitivo")
    discord_users = db.discord_users
    discord_users.remove({})
    discord_users.insert_many(discord_users_list, ordered=False)


######
#Server Status
######
async def get_server_status(server_status):
    document = server_status.find_one()
    await asyncio.sleep(0.01)
    return document


async def update_server_status(record, updates, server_status):
    server_status.update_one({'_id': record['_id']},{
                            '$set': updates
                            }, upsert=False)


#//////////////////////////////////////////////////////////////////////
#//////////////////////////////////////////////////////////////////////
#//////////////////////////////////////////////////////////////////////