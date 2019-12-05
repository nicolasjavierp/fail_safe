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


class MembershipTypeEnum:
    NONE = 0
    XBOX = 1
    PSN = 2
    STEAM = 3
    BLIZZARD = 4
    STADIA = 5
    DEMON = 10
    BUNGIENEXT = 254
    All = -1
 
 
class ComponentTypeEnum:
    NONE = '0'
    PROFILES = '100'
    VENDORRECEIPTS = '101'
    PROFILEINVENTORIES = '102'
    PROFILECURRENCIES = '103'
    PROFILEPROGRESSION = '104'
    PLATFORMSILVER = '105'
    CHARACTERS = '200'
    CHARACTERINVENTORIES = '201'
    CHARACTERPROGRESSIONS = '202'
    CHARACTERRENDERDATA = '203'
    CHARACTERACTIVITIES = '204'
    CHARACTEREQUIPMENT = '205'
    ITEMINSTANCES = '300'
    ITEMOBJECTIVES = '301'
    ITEMPERKS = '302'
    ITEMRENDERDATA = '303'
    ITEMSTATS = '304'
    ITEMSOCKETS = '305'
    ITEMTALENTGRIDS = '306'
    ITEMCOMMONDATA = '307'
    ITEMPLUGSTATES = '308'
    ITEMPLUGOBJECTIVES = '309'
    ITEMREUSABLEPLUGS = '310'
    VENDORS = '400'
    VENDORCATEGORIES = '401'
    VENDORSALES = '402'
    KIOSKS = '500'
    CURRENCYLOOKUPS = '600'
    PRESENTATIONNODES = '700'
    COLLECTIBLES = '800'
    RECORDS = '900'
    TRANSITORY = '1000'
 
 
class StatsEnum:
    HANDICAP = '2341766298'
    VOID_COST = '2399985800'
    VELOCITY = '2523465841'
    RECOIL_DIRECTION = '2715839340'
    SCORE_MULTIPLIER = '2733264856'
    EFFICIENCY = '2762071195'
    SWING_SPEED = '2837207746'
    CHARGE_TIME = '2961396640'
    MOBILITY = '2996146975'
    BOOST = '3017642079'
    POWER_BONUS = '3289069874'
    SOLAR_COST = '3344745325'
    ZOOM = '3555269338'
    ANY_ENERGY_TYPE_COST = '3578062600'
    PRECISION_DAMAGE = '3597844532'
    BLAST_RADIUS = '3614673599'
    ARC_ENERGY_CAPACITY = '3625423501'
    ARC_COST = '3779394102'
    MAGAZINE = '3871231066'
    DEFENSE = '3897883278'
    MOVE_SPEED = '3907551967'
    TIME_TO_AIM_DOWN_SIGHTS = '3988418950'
    IMPACT = '4043523819'
    RELOAD_SPEED = '4188031367'
    STRENGTH = '4244567218'
    ROUNDS_PER_MINUTE = '4284893193'
    VOID_ENERGY_CAPACITY = '16120457'
    INTELLECT = '144602215'
    STABILITY = '155624089'
    DEFENSE = '209426660'
    DURABILITY = '360359141'
    RESILIENCE = '392767087'
    DRAW_TIME = '447667954'
    AMMO_CAPACITY = '925767036'
    HANDLING = '943549884'
    RANGE = '1240592695'
    AIM_ASSISTANCE = '1345609583'
    ATTACK = '1480404414'
    SPEED = '1501155019'
    HEROIC_RESISTANCE = '1546607977'
    ARC_DAMAGE_RESISTANCE = '1546607978'
    SOLAR_DAMAGE_RESISTANCE = '1546607979'
    VOID_DAMAGE_RESISTANCE = '1546607980'
    ACCURACY = '1591432999'
    DISCIPLINE = '1735777505'
    INVENTORY_SIZE = '1931675084'
    POWER = '1935470627'
    RECOVERY = '1943323491'
    SOLAR_ENERGY_CAPACITY = '2018193158'
 
 
class ItemCategoryEnum:
    WARLOCK_GEAR = 21
    TITAN_GEAR = 22
    HUNTER_GEAR = 23
 
 
class BucketEnum:
    ENERGY_WEAPONS = 2465295065
    UPGRADE_POINT = 2689798304
    STRANGE_COIN = 2689798305
    GLIMMER = 2689798308
    LEGENDARY_SHARDS = 2689798309
    SILVER = 2689798310
    BRIGHT_DUST = 2689798311
    SHADERS = 2973005342
    EMOTES = 3054419239
    MESSAGES = 3161908920
    SUBCLASS = 3284755031
    MODIFICATIONS = 3313201758
    HELMET = 3448274439
    GAUNTLET = 3551918588
    FINISHERS = 3683254069
    MATERIALS = 3865314626
    GHOST = 4023194814
    EMBLEMS = 4274335291
    CLAN_BANNERS = 4292445962
    CHEST_ARMOR = 14239492
    SHADERS = 18606351
    LEG_ARMOR = 20886954
    GENERAL = 138197802
    LOST_ITEMS = 215593132
    SHIPS = 284967655
    ENGRAMS = 375726501
    POWER_WEAPONS = 953998645
    EMOTES = 1107761855
    AURAS = 1269569095
    QUESTS = 1345459588
    SPECIAL_ORDERS = 1367666825
    CONSUMABLES = 1469714392
    KINETIC_WEAPONS = 1498876634
    SEASONAL_ARTIFACT = 1506418338
    CLASS_ARMOR = 158578786





@client.command(name='Info Xur',
                description="Entrega la ubicación de Xur en Destiny2",
                brief="Ubicacion Xur",
                aliases=['xur'],
                pass_context=True)
async def xur_info(context):
    #embed = discord.Embed(title=":warning: Warning" , description="Este comando esta en periodo de beta testing, ante cualquier inconveniente informar a un admin. Gracias", color=0x00ff00)
    #await client.send_message(context.message.channel, embed=embed)
    #4 Tests
    #fs = FailSafe(load_param_from_config('BUNGIE_API_KEY'))
    #4 Heroku
    fs = FailSafe(BUNGIE_API_KEY)         #Start Fail_Safe 4 Heroku
    #END Heroku
    user_id = context.message.author.id
    user=await client.get_user_info(user_id)
    await client.say(":white_check_mark: Mensaje directo enviado.")
    if await fs.async_isBungieOnline():
        await client.send_message(user, "Juntando información ... un momento por favor.")
        #await client.say("Juntando información ... un momento por favor.")
        is_xur_here, info, inventory, xur_map = get_xur_info(fs)
        if is_xur_here: 
            url_bungie="http://www.bungie.net/"   
            embed = discord.Embed(title=":squid:__XUR:__", description=info, color=0x00ff00)
            embed.add_field(name='Referencia', value="<https://ftw.in/game/destiny-2/find-xur>", inline=False)
            embed.set_thumbnail(url=client.user.avatar_url.replace("webp?size=1024","png"))
            embed.set_image(url=xur_map)
            await client.send_message(user, embed=embed)
            if inventory and info:
                for idx, val in enumerate(inventory):
                    destiny_class=""
                    index_xur = {0:":gun: **Arma:**",1:":knife: **Cazador:**",2:":punch: **Titan:**",3:":bulb: **Hechicero:**"}
                    destiny_class = index_xur[idx]
                    embed = discord.Embed(title=destiny_class, description="", color=0x00ff00)
                    embed.set_image(url=url_bungie+val)
                    await client.send_message(user, embed=embed)
            else:
                #embed = discord.Embed(title="Error!", description="No pude obtener los datos, intenta mas tarde ...", color=0x00ff00)
                embed = discord.Embed(title="Error!", description="Todavía no esta la info KP@, aguantá la mecha un toque y intenta mas tarde ...", color=0x00ff00)
                await client.send_message(user, embed=embed)
            
        else:
            embed = discord.Embed(title=":x:__XUR:__", description=info, color=0x00ff00)
            embed.set_thumbnail(url=client.user.avatar_url.replace("webp?size=1024","png")) 
            await client.send_message(user, embed=embed)
            #await client.send_message(context.message.channel, embed=embed)
    else:
        embed = discord.Embed(title=":x: Servidores de Destiny estan deshabilitados! Intenta mas tarde ...", description="¯\\_(ツ)_/¯", color=0x00ff00)
        await client.send_message(user, embed=embed)