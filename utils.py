# -*- coding: utf-8 -*-
# Works with Python 3.6

import random
import asyncio
import aiohttp
from discord.ext.commands import Bot
from fail_safe import FailSafe
import os, time
import discord
import re
import json
import pymongo
from datetime import datetime
from boto.s3.connection import S3Connection
import unicodedata
from urllib.request import urlopen
from pymongo import MongoClient
from datetime import timedelta 
from datetime import date 
from db import *


def is_user_in_users(user):
    with open('users.json', 'r') as f:
        users = json.load(f)
        if user.id in users:
            return True
        else:
            return False


def is_clanmate_in_clan(clanmate_battletag):
    #Patch for those who have no battleTag
    with open('clan.json', 'r') as f:
        clan = json.load(f)
        #if clanmate_battletag in clan or name[0] in clan:
        if clanmate_battletag in clan:
            return True
        else:
            return False


async def does_user_have_role(member,rol_id):
    for role in member.roles:
        if rol_id == role.id:
            #print(member.name+" tiene rol " + rol_id + "!")
            return True
    await asyncio.sleep(0.01)
    return False


async def update_discord_user_last_activity(message_author_id):
    #4 tests
    #MONGODB_URI = load_param_from_config('MONGO_DB_MLAB')
    #END tests
    #4 Heroku
    MONGODB_URI = os.environ['MONGO_DB_MLAB']
    #END Heroku
    cursor = MongoClient(MONGODB_URI, connectTimeoutMS=30000)
    db = cursor.get_database("bot_definitivo")
    discord_users = db.discord_users
    currentTime = datetime.now()
    update = {
            "last_activity": currentTime
    }
    original_record = get_one_discord_user(message_author_id, discord_users)
    if original_record:
        update_discord_user(original_record,update,discord_users)
    await asyncio.sleep(0.01)


def load_param_from_config(item):
    THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
    my_config_file = os.path.join(THIS_FOLDER, 'config.json')
    with open(my_config_file, 'r') as f:
        config = json.load(f)
        return config['DEFAULT'][item]


def read_param_from_aux(item):
    THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
    my_config_file = os.path.join(THIS_FOLDER, 'aux.json')
    with open(my_config_file, 'r') as f:
        aux = json.load(f)
        return aux[item]
        #return aux


def increment_param_in_1_aux(item):
    THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
    my_aux_file = os.path.join(THIS_FOLDER, 'aux.json')
    with open(my_aux_file, 'r') as f:
        aux = json.load(f)
        tmp = aux[item]
        aux[item] = tmp+1
    with open("aux.json", "w") as f:
        json.dump(aux, f)


def reset_param_aux(item):
    THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
    my_aux_file = os.path.join(THIS_FOLDER, 'aux.json')
    with open(my_aux_file, 'r') as f:
        aux = json.load(f)
        aux[item] = 0
    with open("aux.json", "w") as f:
        json.dump(aux, f)

def is_user_admin(ctx):
    server = ctx.message.server
    user_id = ctx.message.author.id
    user=server.get_member(user_id)
    for i in server.roles:
        if "Admin" in i.name:
                    admin_id=i.id
    if admin_id in [role.id for role in user.roles]:
        return True
    else:
        return False

def check_queue(id , my_queues, players):
    if my_queues[id]:
        player = my_queues[id].pop(0)
        players[id] = player
        player.start()


def class_race_report(guardian_info, user_destiny_id, raids ):
    for key, value in raids.items():
        #print(key)
        #print(value[0])
        #print("*************************************")
        today = date.today()
        offset = (today.weekday() - 1) % 7
        last_tuesday = today - timedelta(days=offset)
        last_tuesday_temp = str(last_tuesday)+" 17:00:00"
        last_tuesday_reset = datetime.strptime(last_tuesday_temp,"%Y-%m-%d %H:%M:%S")
        #value tiene una lista de las últimas raids ordenados cronologicamente
        raids_complete = []
        for raid in value:
            raid_date_time = datetime.strptime(raid['period'],"%Y-%m-%dT%H:%M:%SZ")
            if raid['values']['completed']['statId']=="completed" and raid_date_time>last_tuesday_reset:
                raids_complete.append(raid)
        print("Raids Completadas despues del reset="+str(len(raids_complete)))
        return raids_complete
    