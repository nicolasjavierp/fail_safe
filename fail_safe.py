# -*- coding: utf-8 -*-
import requests
import os
import humanize
from pymongo import MongoClient
import asyncio
import aiohttp

from utils import *



THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
my_config_file = os.path.join(THIS_FOLDER, 'config.json')
my_clan_file = os.path.join(THIS_FOLDER, 'clan.json')
my_inactive_file = os.path.join(THIS_FOLDER, 'inactive_list.txt')
my_whitelist_file = os.path.join(THIS_FOLDER, 'white_list.txt')

class FailSafe(object):
    '''
    For the API calls below, no authentication is needed. You'll just need to have your Bungie API key exported in your bash profile
    and named as BUNGIE_API_KEY to run the script as-is.
    '''

    def __init__(self, api_key):
        '''
        api_key (str): The api key given to you by Bungie when you registered your app with them
        '''
        self.api_key = api_key
        self.blacklist = []
        #self.our_clans = [(2943900, "Escuadra 2"), (3084439, "Escuadra 3"), (3111393, "Escuadra 4"), (3144839,"Escuadra 5"), (3635441,"Escuadra 6")]
        self.our_clans = [(3144839,"REVENANTS Delta"), (3635441,"REVENANTS Beta"), (2943900, "REVENANTS Lambda"), (3836085, "REVENANTS Epsilon"), (3989167, "REVENANTS Omega")]
        #self.our_clans = [(2943900, "REVENANTS Lambda")] # for tests
        self.error_members = {}
        self.error_members = set()
        self.retrys = []
        self.guardian_class = {3655393761:"Titan", 2271682572:"Hechicero", 671679327:"Cazador"}
        self.guardian_category_gear = {22:"Titan", 21:"Hechicero", 23:"Cazador"}
        self.guardian_race = {2803282938:"Insomne", 898834093:"Exo", 3887404748:"Humano"}
        self.guardian_gender = {3111576190: "Masculino", 2204441813:"Femenino"}
        self.raids = {2122313384: "Ultimo Deseo", 548750096:"Azote del Pasado", 1661734046: "Ultimo Deseo_Guiado", 2214608156: "Ultimo Deseo_58", 2812525063:"Azote del Pasado_Guiado", 3333172150:"Corona del Dolor", 960175301:"Corona del Dolor_Guiada", 2659723068:"Jardin de Salvacion"} #Spire of stars 119944200 // Eater of worlds 3089205900 // Leviathan 89727599
        self.relevant_raids = {0: "Ultimo Deseo", 1:"Azote del Pasado", 2:"Corona del Dolor", 3:"Jardin de Salvacion"}
        self.xur_locations={'IO':['Xur esta en IO en la zona de Cicatriz del Gigante',"https://cdn.discordapp.com/attachments/383420850738823186/565192090347372564/io.jpg"],
                            'TITAN':['Xur esta en Titan en la zona Plataforma',"https://cdn.discordapp.com/attachments/383420850738823186/565192132898586627/titan.jpg"],
                            'EDZ':['Xur esta la Tierra (ZME), en la zona Bahía del Viento',"https://cdn.discordapp.com/attachments/383420850738823186/565192115005423651/tierra.jpg"],
                            'NESSUS':['Xur esta en Nessus en la zona de Tumba del Vigia',"https://cdn.discordapp.com/attachments/383420850738823186/565192144978182144/nessus.jpg"],
                            'TOWER':['Xur esta la Torre en la zona de Hangar detras de Orbita Muerta',"https://cdn.discordapp.com/attachments/383420850738823186/565192126330044430/torre.jpg"]}

    async def get_clan_capacity(self):
        '''Generates Capacity of clans'''
        capacity = []
        for clan in self.our_clans:
            await asyncio.sleep(0.05)
            site_call = "https://www.bungie.net/Platform/GroupV2/" + str(clan[0]) + "/Members/?currentPage=1"
            request = requests.get(site_call, headers={"X-API-Key":self.api_key})
            print(request)
            if request.json():
                my_dict={clan[1]:request.json()['Response']['totalResults']}
                capacity.append(my_dict)
        return capacity


    async def async_get_ClanPlayerList(self, clan):
        '''Generates list of dicts of all players with membersip id, profile and clan name currently in Clan corresponding with clan id'''
        temp_list = []
        site_call = "https://www.bungie.net/Platform/GroupV2/" + str(clan[0]) + "/Members/?currentPage=1"
        #request = requests.get(site_call, headers={"X-API-Key":self.api_key})
        headers={"X-API-Key":self.api_key}
        async with aiohttp.ClientSession() as session:
            async with session.get(site_call,headers=headers) as request:
                if request.status == 200:
                    json = await request.json()
                    #print(type(json))
                    #print(json.keys)
                    for item in json['Response']['results']:
                        #print(item)
                        #print(str(item['destinyUserInfo']['membershipId']))
                        #print(item["destinyUserInfo"]["membershipId"], item["destinyUserInfo"]["displayName"])
                        if 'bungieNetUserInfo' in item:
                        #if item["bungieNetUserInfo"]["membershipId"]:
                            clanmate_dict = {'membershipId':item['destinyUserInfo']['membershipId'], 'displayName':item['destinyUserInfo']['displayName'], "bungie_id":item["bungieNetUserInfo"]["membershipId"], "battletag":""}
                        else:
                            clanmate_dict = {'membershipId':item['destinyUserInfo']['membershipId'], 'displayName':item['destinyUserInfo']['displayName'], "bungie_id":None, "battletag":item['destinyUserInfo']['displayName']}
                        #clanmate_dict = {'membershipId':item['destinyUserInfo']['membershipId'], 'displayName':item['destinyUserInfo']['displayName'], "bungie_id":item["bungieNetUserInfo"]["membershipId"]}
                        temp_list.append(clanmate_dict)
                return temp_list


    async def async_get_item_info(self, itemHash):
            '''Get Async info on item manifest in Destiny 2'''
            site_call = "http://www.bungie.net/platform/Destiny2/Manifest/DestinyInventoryItemDefinition/" + itemHash
            headers={"X-API-Key":self.api_key}
            async with aiohttp.ClientSession() as session:
                async with session.get(site_call,headers=headers) as request:
                    if request.status == 200:
                        #print(request.status)
                        data = await request.json()
                        return (data['Response'])
                    else:
                        #print(request.status)
                        return None


    async def async_get_playerBySteamTag(self, steam_tag):
        '''Get Async Destiny 2 info on steam tag'''
        site_call = "https://www.bungie.net/Platform/Destiny2/SearchDestinyPlayer/3/" + steam_tag
        headers={"X-API-Key":self.api_key}
        async with aiohttp.ClientSession() as session:
            async with session.get(site_call,headers=headers) as request:
                if request.status == 200:
                    data = await request.json()
                    return data['Response']
                else:
                    return None


    async def async_get_DestinyUserProfileDetail(self, membership_id):
        '''
        membership_id (int): the Destiny membership_id of a player (returned by get_DestinyUserId)
        components (list of ints): the type of info you want returned according the Bungie API docs.
        Defaults to 100: basic profile info ([100, 200] would also return more detailed info by Destiny character
        Uses new Destiny 2 endpoint for PC player using the Destiny membershipId.

        Get Destiny 2 user profile'''
        site_call = "https://bungie.net/Platform/Destiny2/3/Profile/"+membership_id+"/?components=100,200"
        headers={"X-API-Key":self.api_key}
        async with aiohttp.ClientSession() as session:
            async with session.get(site_call,headers=headers) as request:
                if request.status == 200:
                    data = await request.json()
                    return data['Response']
                else:
                    return None


    async def async_get_CharactersRaids(self, membership_id, character_id):
        '''
        get_CharactersRaids
        None: 0
        Story: 2
        Strike: 3
        Raid: 4
        AllPvP: 5
        Patrol: 6
        AllPvE: 7
        Reserved9: 9
        Control: 10
        Reserved11: 11
        Clash: 12
        Clash -> Destiny's name for Team Deathmatch. 4v4 combat, the team with the highest kills at the end of time wins.
        Reserved13: 13
        CrimsonDoubles: 15
        Nightfall: 16
        HeroicNightfall: 17
        AllStrikes: 18
        IronBanner: 19
        Reserved20: 20
        Reserved21: 21
        Reserved22: 22
        Reserved24: 24
        AllMayhem: 25
        Reserved26: 26
        Reserved27: 27
        Reserved28: 28
        Reserved29: 29
        Reserved30: 30
        Supremacy: 31
        PrivateMatchesAll: 32
        Survival: 37
        Countdown: 38
        TrialsOfTheNine: 39
        Social: 40
        TrialsCountdown: 41
        TrialsSurvival: 42
        IronBannerControl: 43
        IronBannerClash: 44
        IronBannerSupremacy: 45
        ScoredNightfall: 46
        ScoredHeroicNightfall: 47
        Rumble: 48
        AllDoubles: 49
        Doubles: 50
        PrivateMatchesClash: 51
        PrivateMatchesControl: 52
        PrivateMatchesSupremacy: 53
        PrivateMatchesCountdown: 54
        PrivateMatchesSurvival: 55
        PrivateMatchesMayhem: 56
        PrivateMatchesRumble: 57
        HeroicAdventure: 58
        Showdown: 59
        Lockdown: 60
        Scorched: 61
        ScorchedTeam: 62
        Gambit: 63
        AllPvECompetitive: 64
        Breakthrough: 65
        BlackArmoryRun: 66
        Salvage: 67
        IronBannerSalvage: 68
        PvPCompetitive: 69
        PvPQuickplay: 70
        ClashQuickplay: 71
        ClashCompetitive: 72
        ControlQuickplay: 73
        ControlCompetitive: 74
        GambitPrime: 75
        Reckoning: 76
        '''
        site_call = "https://www.bungie.net/platform/Destiny2/3/Account/"+ str(membership_id)+"/Character/"+str(character_id)+"/Stats/Activities/?count=250&mode=4&page=0"
        request = requests.get(site_call,headers={"X-API-Key":self.api_key})
        #print("Player Raids:")
        #print("=============")
        #print(request.json()['Response'])
        if request.json()['Response']:
            return request.json()['Response']
        else:
            return None


    async def async_get_XurInventory(self):
        '''Calls the api with Xurs inventory'''
        site_call = "http://bungie.net/Platform/Destiny2/Vendors/?components=402"
        #request = requests.get(site_call, headers={"X-API-Key":self.api_key})
        xurs_items_ids = []
        headers={"X-API-Key":self.api_key}
        async with aiohttp.ClientSession() as session:
            async with session.get(site_call,headers=headers) as request:
                if request.status == 200:
                    print(request.status)
                    data = await request.json()
                    #print(type(data))
                    #print(data)
                    vendor_list = data['Response']['sales']['data']['2190858386']['saleItems']
                    #print(type(vendor_list))
                    vendor_temp = json.dumps(vendor_list)
                    vendor_data = json.loads(vendor_temp)
                    #print(type(vendor_data))
                    #print(vendor_data.keys)
                    for key, value in vendor_data.items():
                        #Filtering out 5 of swords
                        if value['costs']:
                            #print(value)              
                            xurs_items_ids.append(value)
                    #print("=====================")
                    #print(xurs_items_ids)
                    #print("=====================")
                    return xurs_items_ids
                else:
                    print(request.status)
                    #print(request.status)
                    return None


    async def async_isBungieOnline(self):
        '''Generates list of dicts of all players with membersip id, profile and clan name currently in Clan corresponding with clan id'''
        #print(self.our_clans[2][0])
        site_call = "https://www.bungie.net/Platform/GroupV2/" + str(self.our_clans[2][0])
        headers={"X-API-Key":self.api_key}
        async with aiohttp.ClientSession() as session:
        #async with aiohttp.ClientSession() as session:
            async with session.get(site_call,headers=headers) as request:
                if request.status == 200:
                    #print(request.status)
                    return True
                else:
                    #print(request.status)
                    return False     


    async def async_get_Clanmate_LastPlayed(self, clanmember_membership_id):
        site_call = "https://bungie.net/Platform/Destiny2/3/Profile/" +clanmember_membership_id+ "/" + "?components=100,200"
        headers={"X-API-Key":self.api_key}
        #jar = aiohttp.CookieJar(unsafe=True)
        #async with aiohttp.ClientSession(cookie_jar=jar) as s:
        async with aiohttp.ClientSession() as session:
            async with session.get(site_call,headers=headers) as request:
                if request.status == 200:
                    try:
                        json = await request.json()
                        if json['Response']['profile']['data']['dateLastPlayed']:
                            #print("GOT LAST PLAYED FOR: "+str(clanmember_membership_id))
                            return json['Response']['profile']['data']['dateLastPlayed']
                        else:
                            #print("RETRY: Response 200 but no data")
                            return None
                    except Exception as ex:
                        print("Console Player:"+clanmember_membership_id)
                        return None
                
                
    async def async_add_Clanmembers_LastPlayed(self, clan_list):
        for clanmember in clan_list:
            await asyncio.sleep(1)
            last_played = await self.async_get_Clanmate_LastPlayed(clanmember["membershipId"])
            #print("Player "+str(clanmember['displayName'])+" "+str(clanmember['membershipId'])+ " last played on "+ str(last_played))
            if last_played:
                clanmember["platform"] = "PC"
                clanmember["last_played"] = last_played
            else:
                clanmember["platform"] = "Console"
                clanmember["last_played"] = None
        #print(clan_list)
        return clan_list


    async def async_get_Clanmate_ClanName(self, clanmember_membership_id):
        '''Gets the players clan name'''
        site_call = "https://www.bungie.net/Platform/GroupV2/User/3/{}/0/1/".format(str(clanmember_membership_id))
        headers={"X-API-Key":self.api_key}
        async with aiohttp.ClientSession() as session:
            async with session.get(site_call,headers=headers) as request:
                if request.status == 200:
                    json = await request.json()
                    if json['Response']['results']:
                        return json['Response']['results'][0]['group']['name']
                    else:
                        return None
                else:
                    return None


    async def async_add_Clanmembers_ClanName(self, clan_list):
        '''Adds the players clan name'''
        for clanmember in clan_list:
            await asyncio.sleep(1)
            if clanmember['platform'] is "PC":
                clan_name = await self.async_get_Clanmate_ClanName(clanmember["membershipId"])
                clanmember["clan"] = clan_name
            else:
                clanmember["clan"] = None
        return clan_list


    async def async_add_Clanmembers_Battletag(self, clan_list):
        '''Adds the players clan name'''
        for clanmember in clan_list:
            await asyncio.sleep(1)
            if (clanmember['platform'] is "PC") and clanmember['bungie_id']:
                battletag = await self.async_get_Clanmate_Battletag(clanmember["bungie_id"])
                if battletag:
                    clanmember["battletag"] = battletag
                else:
                    clanmember["battletag"] = clanmember["displayName"]
            else:
                clanmember["battletag"] = clanmember["displayName"]
        return clan_list


    async def async_get_Clanmate_Battletag(self, bungie_id):
        '''Adds the players battletag'''
        site_call = "http://www.bungie.net/platform/User/GetBungieAccount/" + bungie_id + "/254"
        headers={"X-API-Key":self.api_key}
        async with aiohttp.ClientSession() as session:
            async with session.get(site_call,headers=headers) as request:
                if request.status == 200:
                    json = await request.json()
                    #print(json)
                    if 'bungieNetUser' in json['Response']:
                    #if json['Response']["bungieNetUser"]["blizzardDisplayName"]:
                        #print(str(json['Response']["bungieNetUser"]["blizzardDisplayName"]))
                        return json['Response']["bungieNetUser"]["blizzardDisplayName"]
                    else:
                        return None


    async def async_is_blacklisted(self, player):
        '''Checks if player is a blacklister'''
        #print(player)
        if player['last_played']:
            #break_point_seconds=1296000*2
            break_point_seconds=1814400
            last = player['last_played']
            last_played = datetime.strptime(last, "%Y-%m-%dT%H:%M:%SZ")
            now = datetime.utcnow().replace(microsecond=0)
            diff = now - last_played
            human_diff = humanize.naturaltime(diff)
            delta_seconds = diff.total_seconds()
            #print("----------------PLAYER----------------------")
            #print(human_diff, player, delta_seconds)
            #print("---------------------------------------------")
            if (delta_seconds > break_point_seconds):
                #print("Blacklisted")
                #player["inactive_time"] = human_diff
                temp_num = "{0:.2f}".format(delta_seconds/break_point_seconds)
                player["inactive_time"] = str(temp_num)+" meses"
                #player["inactive_time"] = delta_seconds
                player["date"] = datetime.today().strftime('%Y-%m-%d')
                return player
            else:
                #print("NOT Blacklisted")
                return None
        else:
            return None


    async def async_filter_blacklist(self, player_list):
        '''Filters special players from blacklist'''
        #4 tests
        #with open(my_config_file, 'r') as f:
        #    config = json.load(f)
        #MONGODB_URI = load_param_from_config('MONGO_DB_MLAB')
        #END tests
        #4 Heroku
        MONGODB_URI = os.environ['MONGO_DB_MLAB']
        #END Heroku
        client = MongoClient(MONGODB_URI, connectTimeoutMS=30000)
        db = client.get_database("bot_definitivo")
        whitelist = db.whitelist
        definitive_blacklist = []
        for player in player_list:
            if not(await self.get_one_Clanmate_Whitelist(player['displayName'], whitelist)):
                #print("Player"+str(player['displayName'])+" NOT in Whitelist adding to definitive list")
                definitive_blacklist.append(player)
            else:
                print("Player"+str(player['displayName'])+" in Whitelist !! Special player detected.")
        #print(str(definitive_blacklist))
        return definitive_blacklist


    async def get_one_Clanmate_Whitelist(self, clanmate_displayName, whitelist):
        '''Returns whitelister'''
        document = whitelist.find_one({'displayName':clanmate_displayName})
        return document


    async def async_push_blacklist(self, definitive_blacklist):
        '''Pushes blacklist to db'''
        #4 tests
        #with open(my_config_file, 'r') as f:
        #    config = json.load(f)
        #MONGODB_URI = load_param_from_config('MONGO_DB_MLAB')
        #END tests
        #4 Heroku
        MONGODB_URI = os.environ['MONGO_DB_MLAB']
        #END Heroku
        client = MongoClient(MONGODB_URI, connectTimeoutMS=30000)
        db = client.get_database("bot_definitivo")
        blacklist = db.blacklist
        
        blacklist.insert_many(definitive_blacklist, ordered=False)
        #for member in definitive_blacklist:
        #    print("Pusshing "+str(member))
        #    self.push_blacklister_to_db(member,blacklist)


    async def async_push_clanmates_to_db(self, clan_list):
        '''Pushes clanmates to db'''
        #4 tests
        #with open(my_config_file, 'r') as f:
        #    config = json.load(f)
        #MONGODB_URI = load_param_from_config('MONGO_DB_MLAB')
        #END tests
        #4 Heroku
        MONGODB_URI = os.environ['MONGO_DB_MLAB']
        #END Heroku
        client = MongoClient(MONGODB_URI, connectTimeoutMS=30000)
        db = client.get_database("bot_definitivo")
        clanmates = db.clan_members
        if clan_list:
            clanmates.insert_many(clan_list, ordered=False)
        else:
            print("Empty Clanmate list .... not pushing to db")


    async def async_clear_clanmates_blacklister_db(self):
        '''Pushes clanmates to db'''
        print("Clearing Blacklist and Clanmates ...")
        #4 tests
        #with open(my_config_file, 'r') as f:
        #    config = json.load(f)
        #MONGODB_URI = load_param_from_config('MONGO_DB_MLAB')
        #END tests
        #4 Heroku
        MONGODB_URI = os.environ['MONGO_DB_MLAB']
        #END Heroku
        client = MongoClient(MONGODB_URI, connectTimeoutMS=30000)
        db = client.get_database("bot_definitivo")
        clanmates = db.clan_members
        blacklist = db.blacklist
        #removes all documents from clanmates
        clanmates.remove({})
        #removes all documents from blacklisters
        blacklist.remove({})
        print("Cleared Blacklist and Clanmates!")


    def get_manifest_item_info(self, itemHash):
        '''Get info on item manifest in Destiny 2'''
        site_call = "http://www.bungie.net/platform/Destiny2/Manifest/DestinyInventoryItemDefinition/" + itemHash
        request = requests.get(site_call,
                                headers={"X-API-Key":self.api_key})
        if request:
            return request.json()['Response']
        else:
            return None


    async def async_get_Xur_info(self, xur_api_key):
        '''Gets Xurs location ID'''
        site_call = "https://api.xur.wiki/?api_key={}&user_id=nicolas".format(xur_api_key)
        async with aiohttp.ClientSession() as session:
            async with session.get(site_call) as request:
                if request.status == 200:
                    json = await request.json()
                    if json['location_id']:
                        return json
                    else:
                        return None
                else:
                    return None
