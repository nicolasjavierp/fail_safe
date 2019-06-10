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
import requests  
from bs4 import BeautifulSoup

try:
    from urllib import parse as urllib_parse
except ImportError:
	import urlparse as urllib_parse

my_reset_time='1700'

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
    for key, value in fs.relevant_raids.items():
        #unique_raid_complete[value] = False
        #print(value)
        unique_raid_complete[str(value)]=False
    #print(filter_completed_raids)
    for raid in filtered_completed_raids:
        #print(raid)
        for key, value in fs.relevant_raids.items():
            if value in str(fs.raids[raid['activityDetails']['directorActivityHash']]):
                unique_raid_complete[str(value)]=True
        #print(str(fs.raids[raid['activityDetails']['directorActivityHash']]))
        #unique_raid_complete[str(fs.raids[raid['activityDetails']['directorActivityHash']])]=True
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


def get_xur_info(fs):
    r = requests.get('https://ftw.in/game/destiny-2/find-xur')
    soup = BeautifulSoup(r.text, 'html.parser')
    links_with_text = []
    inventory = []
    for a in soup.find_all('a', href=True): 
        if a.text: 
            links_with_text.append(a['href'])
        if "DestinyInventoryItemDefinition" in a['href'] or "Explore/Detail/Item" in a['href']:
            #print(a['href'])
            inventory.append(re.sub("\D", "", a['href']))
    #print(links_with_text)
    ps = soup.find_all('p')
    xur_info = "??????"
    item_icons = []
    now = datetime.now()
    if (now.weekday() == 0) or ((now.weekday() == 1) and (now.time() <= datetime.strptime('1700','%H%M').time())) or (now.weekday() == 4 and (now.time() >= datetime.strptime('1700','%H%M').time())) or (now.weekday() == 5) or (now.weekday() == 6):
        #print("XUR esta !!")
        if inventory:
            for x in inventory:
                item = fs.get_manifest_item_info(x)
                if item:
                    #print("Item manifest FOUND: ")
                    #print(item['displayProperties']['icon'])
                    item_icons.append(item['displayProperties']['icon'])
                else:
                    print("Could not get item manifest")
        else:
            print("Inventory NULL")
        #print(xur_location)
        xur_map = None
        xur_info = None
        if ps and len(ps)>=2:
            for key ,value in fs.xur_locations.items():
                if key in ps[1].text.upper():
                    #print("Detectado:"+ str(key))
                    xur_location = value[0]
                    xur_map = value[1]
                    xur_departure_temp = ps[1].text.split("reset on",1)[1] 
                    xur_departure_temp =  xur_departure_temp[:-1]
                    #print(xur_departure_temp)
                    xur_departure = (datetime.strptime(xur_departure_temp, " %B %d").strftime("%d-%m"))
                    #print(xur_departure)
            if xur_location and xur_departure:
                xur_info = str(xur_location)+" y se va el reset del "+str(xur_departure)
                return True, str(xur_info), item_icons, xur_map
            else:
               True, None, None, None 
    else:
        return False, "Xur solamente esta de Viernes a Martes. Proxima aparición será el reset del "+str(get_last_friday_reset().date()+timedelta(weeks=1)), None, None


def get_random_lore():
    posible_contents=[]
    excluded_contents=["Shank", "Ogre"] 
    enemy_contents_url = "https://destiny.fandom.com/es/wiki/Categoría:Enemigos"
    result = requests.get(enemy_contents_url)
    if result:
        result.encoding = 'utf-8'
        soup = BeautifulSoup(result.content, 'html.parser')

        for link in soup.findAll('div', {'class': 'category-page__members'}):
            for a in link.find_all('a', href=True):
                temp_link = urllib_parse.unquote(a['href'])
                temp_list = temp_link.split("/")
                #print(temp_list[-1])
                if temp_list[-1] not in excluded_contents:
                    posible_contents.append(temp_list[-1])
                #else:
                #    print("Found Excluded content: "+str(temp_list[-1]))
        extras = ["El_Viajero", "Guardianes", "Exo", "Insomnes", "Humanos"]
        definitive_contents = posible_contents + extras
        lore=[]
        random_value = random.choice(definitive_contents)
        #print("Entrada  =  "+ str(random_value))
        result = requests.get("https://destiny.fandom.com/es/wiki/"+random_value)
        if result:
            c = result.content
            soup = BeautifulSoup(c, 'html.parser')
            lore = ""
            all_p = soup.find("div", {"id":"mw-content-text"}).findAll('p')
            for index, item in enumerate(all_p):
                temp_lore = unicodedata.normalize('NFKD', item.text)#.encode('ASCII', 'ignore')
                formated_lore = re.sub(r'\[[^)]*\]', '', temp_lore)
                lore = lore + formated_lore

            my_list = lore.split("\n")
            definitive_lore = []
            for val in my_list:
                if "." not in val and "?" not in val and "!" not in val and "<<" not in val:
                    pass
                else:
                    definitive_lore.append(val)

            lore = " ".join(definitive_lore)

            #print("-----------")
            #print(lore)
            #print("-----------")

            img_url = [img['src'] for img in soup.find_all('img')]
            #print(img_url[1])
            return random_value,lore,img_url[1]
        else:
            return None,None,None
    else:
        return None,None,None