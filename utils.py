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
from datetime import date# , time

from db import *
import requests  
from bs4 import BeautifulSoup


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


def get_completed_raids(guardian_info, user_destiny_id, raids ):
    for key, value in raids.items():
        #print(key)
        #print(value[0])
        #print("*************************************")
        last_tuesday_reset = get_last_tuesday_reset()
                #print("Last Friday!!:"+str(get_last_friday_reset()))
        #value tiene una lista de las últimas raids ordenados cronologicamente
        raids_complete = []
        for raid in value:
            raid_date_time = datetime.strptime(raid['period'],"%Y-%m-%dT%H:%M:%SZ")

            if raid['values']['completed']['basic']['value']==1 and  raid['values']['completionReason']['basic']['value']==0 and raid_date_time>last_tuesday_reset:
                #print("**************ACTIVE RAIDS**************")
                #print(raid_date_time)
                #print(last_tuesday_reset)
                #print("*************************************")
                raids_complete.append(raid)
        #print("Raids Completadas despues del reset="+str(len(raids_complete)))
        return raids_complete


def filter_completed_raids(raids_complete, fs):
    filtered_completed_raids=[]
    for raid in raids_complete:
            if raid['activityDetails']['referenceId'] in fs.raids:
                filtered_completed_raids.append(raid)
    return filtered_completed_raids
                

def get_unique_raids(filtered_completed_raids, fs):
    unique_raid_complete = {}
    for key, value in fs.raids.items():
        unique_raid_complete[value] = False
    for raid in filtered_completed_raids:
        unique_raid_complete[str(fs.raids[raid['activityDetails']['directorActivityHash']])]=True 
    #print(unique_raid_complete)
    return unique_raid_complete


def get_last_tuesday_reset():
    import datetime
    current_time = datetime.datetime.now()
    # get tuesday, one week ago, at 17 o'clock
    last_tuesday = (current_time.date()
        - datetime.timedelta(days=current_time.weekday())
        + datetime.timedelta(days=1, weeks=-1))
    #print("Last tuesday temp: "+str(last_tuesday))
    last_tuesday_at_17 = datetime.datetime.combine(last_tuesday, datetime.time(17))
    # if today is also tuesday, and after 17 o'clock, change to the current date
    one_week = datetime.timedelta(weeks=1)
    if current_time - last_tuesday_at_17 >= one_week:
        #print("RESTET is now and Greater than one week ... adjusting date!!")
        last_tuesday_at_17 += one_week
    else:
        pass
        #print("Almost a week ago "+str(current_time - last_tuesday_at_17))
    return last_tuesday_at_17


def get_last_friday_reset():
    import datetime
    current_time = datetime.datetime.now()
    # get friday, one week ago, at 17 o'clock
    last_friday = (current_time.date()
        - datetime.timedelta(days=current_time.weekday())
        + datetime.timedelta(days=4, weeks=-1))
    #print("Last Friday temp:"+str(last_friday))
    #print(type(last_friday))
    last_friday_at_17 = datetime.datetime.combine(last_friday, datetime.time(17))
    # if today is also friday, and after 17 o'clock, change to the current date
    one_week = datetime.timedelta(weeks=1)
    if current_time - last_friday_at_17 >= one_week:
        last_friday_at_17 += one_week
    return last_friday_at_17


def is_xur_arround():
    today = date.today()
    if today.weekday() not in [1,2,3] and today<get_last_tuesday_reset():# or today>last_friday_reset:
        pass


def get_xur_info():
    r = requests.get('https://ftw.in/game/destiny-2/find-xur')
    #print r
    soup = BeautifulSoup(r.text, 'html.parser')
    #print "SOUP:"+str(soup)
    results = soup.find_all('div', attrs={'class':'target-class clearfix'})

    records = []  
    for result in results:  
        #print result
        #print(type(result))
        #print(dir(result))
        #print("%%%%%%%%%%%%%%%%%%%%%%%%%")
        #print(type(result.text))
        #print(dir(result.text))
        #print result.text
        now = datetime.now()
        date = result.find('h4').text
        #print str(date)
        date_xur = datetime.strptime(date, '%B %d, %Y')
        print(type(date_xur))
        print(date_xur)
        #print(type(datetime.time(17)))
        reset_time = datetime.strptime('1700','%H%M').time()
        xur_arrival = datetime.combine(date_xur, reset_time)
        #print("XUR!!")
        #print(str(xur_arrival))
        print("----------------------")
        print("Last Monday:")
        print(get_last_tuesday_reset() - timedelta(days=1))
        print("----------------------")
        print(now)#-timedelta(days=1)
        print("----------------------")
        print("Last Friday:")
        print(get_last_friday_reset())#+timedelta(weeks=1))
        print("----------------------")

        if (now.weekday() == 0 and (now.time() <= datetime.time(17))) or (now.weekday() == 4 and (now.time() >= datetime.time(17))) or (now.weekday() == 5) or (now.weekday() == 6):
            print("XUR esta !!")
            xur_location = result.find('p').text
            for i in xur_location:
                print(i)
            return True,  "Xur esta en ... "
        else:
            return False, "KPO, Xur no llega hasta "+str(get_last_friday_reset()+timedelta(weeks=1))
            
        
