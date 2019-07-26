# -*- coding: utf-8 -*-
import requests
import os
from datetime import datetime
from datetime import timedelta
import time
import humanize
import smtplib
import sys
import json
from pymongo import MongoClient
import asyncio
import aiohttp


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
        self.our_clans = [(3144839,"REVENANTS Δ"), (3635441,"REVENANTS β"), (2943900, "REVENANTS Σ")]
        #self.our_clans = [(2943900, "Escuadra 2")] # for tests
        self.error_members = {}
        self.error_members = set()
        self.retrys = []
        self.guardian_class = {3655393761:"Titan", 2271682572:"Hechicero", 671679327:"Cazador"}
        self.guardian_race = {2803282938:"Insomne", 898834093:"Exo", 3887404748:"Humano"}
        self.guardian_gender = {3111576190: "Masculino", 2204441813:"Femenino"}
        self.raids = {2122313384: "Ultimo Deseo", 548750096:"Azote del Pasado", 1661734046: "Ultimo Deseo_Guiado", 2214608156: "Ultimo Deseo_58", 2812525063:"Azote del Pasado_Guiado", 3333172150:"Corona del Dolor", 960175301:"Corona del Dolor_Guiada"} #Spire of stars 119944200 // Eater of worlds 3089205900 // Leviathan 89727599
        self.relevant_raids = {0: "Ultimo Deseo", 1:"Azote del Pasado", 2:"Corona del Dolor"}
        self.xur_locations={'IO':['Xur esta en IO en la zona de Cicatriz del Gigante',"https://cdn.discordapp.com/attachments/383420850738823186/565192090347372564/io.jpg"],
                            'TITAN':['Xur esta en Titan en la zona Plataforma',"https://cdn.discordapp.com/attachments/383420850738823186/565192132898586627/titan.jpg"],
                            'EDZ':['Xur esta la Tierra (ZME), en la zona Bahía del Viento',"https://cdn.discordapp.com/attachments/383420850738823186/565192115005423651/tierra.jpg"],
                            'NESSUS':['Xur esta en Nessus en la zona de Tumba del Vigia',"https://cdn.discordapp.com/attachments/383420850738823186/565192144978182144/nessus.jpg"],
                            'TOWER':['Xur esta la Torre en la zona de Hangar detras de Orbita Muerta',"https://cdn.discordapp.com/attachments/383420850738823186/565192126330044430/torre.jpg"]}


    def get_playerByTagName(self, gamertag):
        '''gamertag (str): The PC gamertag a player uses on Destiny 2'''
        site_call = "https://www.bungie.net/Platform/Destiny2/SearchDestinyPlayer/4/" + gamertag
        request = requests.get(site_call,
                                headers={"X-API-Key":self.api_key})
        if request:
            return request.json()['Response']
        else:
            return None


    def get_manifest_item_info(self, itemHash):
        '''Get info on item manifest in Destiny 2'''
        site_call = "http://www.bungie.net/platform/Destiny2/Manifest/DestinyInventoryItemDefinition/" + itemHash
        request = requests.get(site_call,
                                headers={"X-API-Key":self.api_key})
        if request:
            return request.json()['Response']
        else:
            return None


    def get_battleTag_from_bungieNetUser(self, bungie_id):
        '''Returns the players battletag from bungieNetUser'''
        #print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
        #print(bungie_id)
        site_call = "http://www.bungie.net/platform/User/GetBungieAccount/" + bungie_id + "/254"
        request = requests.get(site_call,
                                headers={"X-API-Key":self.api_key})
        if request:
            #print(request.json())
            return request.json()['Response']
        else:
            return None
    
    
    def get_DestinyUserId(self, gamertag):
        '''gamertag (str): The PC gamertag a player uses on Destiny 2'''
        info = self.get_playerByTagName(gamertag)
        if info:
            return int(info[0]['membershipId'])
        else:
            return None


    def get_BungieUserId(self, membership_id):
        '''
        membership_id (int): the Destiny membership_id of a player (the id returned by get_DestinyUserId)
        Uses old Destiny endpoint for a PC user to get the BUNGIE membershipId
        '''
        site_call = "https://bungie.net/Platform/User/GetMembershipsById/" + str(membership_id) + "/2/"
        request = requests.get(site_call,
                                headers={"X-API-Key":self.api_key})
        return int(request.json()['Response']['bungieNetUser']['membershipId'])

 
    def get_DestinyUserProfile(self, membership_id, components=[100]):
        '''
        membership_id (int): the Destiny membership_id of a player (returned by get_DestinyUserId)
        components (list of ints): the type of info you want returned according the Bungie API docs.
        Defaults to 100: basic profile info ([100, 200] would also return more detailed info by Destiny character
        Uses new Destiny 2 endpoint for PC player using the Destiny membershipId
        '''
        #print membership_id
        #while True:
        try:
            components = "?components=" + ','.join([str(c) for c in components])
            site_call = "https://bungie.net/Platform/Destiny2/4/Profile/" + str(membership_id) + "/" + components
            request = requests.get(site_call, headers={"X-API-Key":self.api_key})
            if request.json()['ErrorCode']==1:
                return request.json()['Response']
            if request.json()['ErrorCode']==217:
                print (str(request.json()['ErrorCode'])+" For membership_id: "+str(membership_id))
                self.error_members.add(membership_id)
                return None
        except Exception as inst:
            self.retrys.append(membership_id)
            #print("----------------------")
            print ("ERROR:"+membership_id)
            #print("----------------------")
            time.sleep(5)
            #print(type(inst))
            return None


    def get_DestinyUserProfileDetail(self, membership_id, components=[200]):
        '''
        membership_id (int): the Destiny membership_id of a player (returned by get_DestinyUserId)
        components (list of ints): the type of info you want returned according the Bungie API docs.
        Defaults to 100: basic profile info ([100, 200] would also return more detailed info by Destiny character
        Uses new Destiny 2 endpoint for PC player using the Destiny membershipId
        '''
        #print membership_id
        #while True:
        try:
            components = "?components=" + ','.join([str(c) for c in components])
            site_call = "https://bungie.net/Platform/Destiny2/4/Profile/" + str(membership_id) + "/" + components
            request = requests.get(site_call, headers={"X-API-Key":self.api_key})
            if request.json()['ErrorCode']==1:
                return request.json()['Response']
            if request.json()['ErrorCode']==217:
                print (str(request.json()['ErrorCode'])+" For membership_id: "+str(membership_id))
                self.error_members.add(membership_id)
                return None
        except Exception as inst:
            self.retrys.append(membership_id)
            #print("----------------------")
            print ("ERROR:"+membership_id)
            #print("----------------------")
            time.sleep(5)
            #print(type(inst))
            return None


    def get_CharactersRaids(self, membership_id, character_id):
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
        site_call = "https://www.bungie.net/platform/Destiny2/4/Account/"+ str(membership_id)+"/Character/"+str(character_id)+"/Stats/Activities/?count=250&mode=4&page=0"
        request = requests.get(site_call,
                                headers={"X-API-Key":self.api_key})
        return request.json()['Response']

    def get_CharactersPVP(self, membership_id, character_id):
        '''
        AllPvP: 5
        '''
        site_call = "https://www.bungie.net/platform/Destiny2/4/Account/"+ str(membership_id)+"/Character/"+str(character_id)+"/Stats/Activities/?count=250&mode=4&page=0"
        request = requests.get(site_call,
                                headers={"X-API-Key":self.api_key})
        return request.json()['Response']

    def get_postGameStats(self, game_id):
        '''game_id (int): Need to look further into this, but game_ids can be found'''
        site_call = "https://bungie.net/Platform/Destiny2/Stats/PostGameCarnageReport/" + str(game_id)
        request = requests.get(site_call,
                                headers={"X-API-Key":self.api_key})
        return request.json()['Response']


    def get_Manifest(self):
        site_call = "https://bungie.net/Platform/Destiny2/Manifest/"
        request = requests.get(site_call,
                                headers={"X-API-Key":self.api_key})
        return request.json()['Response']

  
    def get_PlayerStats(self, membership_id):
        site_call = "https://bungie.net/Platform/Destiny2/2/Account/" + str(membership_id) + "/Stats/"
        request = requests.get(site_call,
                                headers={"X-API-Key":self.api_key})
        return request.json()['Response']


    def get_StatDefinitions(self):
        site_call = "https://bungie.net/Platform/Destiny2/Stats/Definition/"
        request = requests.get(site_call,
                                headers={"X-API-Key":self.api_key})
        return request.json()['Response']


    def get_PlayerClanName(self, membership_id):
            '''Returns the players clan name'''
            if membership_id:
                site_call = "https://www.bungie.net/Platform/GroupV2/User/4/{}/0/1/".format(str(membership_id))
                request = requests.get(site_call,
                                        headers={"X-API-Key":self.api_key})
                if request.json()['Response']['results']:
                    return request.json()['Response']['results'][0]['group']['name']
                else:
                    return None
            else:
                return None

   
    def get_PlayerLastLogin(self, membership_id):
            '''Last time player logged in to Destiny 2'''
            info = self.get_DestinyUserProfile(membership_id)
            if info:
                return info['profile']['data']['dateLastPlayed']
            else:
                return None

    
    def format_PlayerBattleTag(self, battle_tag):
            '''Bungie's api does not undertand the symbol # so you have to encode it like %23
            So Javu#2632 is Javu%232632'''
            return battle_tag.replace('#', '%23')


    def is_blacklisted(self, player):
            #break_point_seconds=1296000
            break_point_seconds=2592000
            for key in player:
                #last = self.get_PlayerLastLogin(key)
                last = player[key][1]['profile']['data']['dateLastPlayed']
                last_played = datetime.strptime(last, "%Y-%m-%dT%H:%M:%SZ")
            now = datetime.utcnow().replace(microsecond=0)
            diff = now - last_played
            human_diff = humanize.naturaltime(diff)
            #print("----------------PLAYER----------------------")
            #print(human_diff, player)
            #print("---------------------------------------------")
            delta_seconds = diff.total_seconds()
            if (delta_seconds > break_point_seconds):
                #print "Blacklisted"
                for key in player:
                    player[key].append(human_diff)
                return True
            else:
                #print "NOT Blacklisted"
                return False
    

    def get_ClanPlayerList(self, clan):
            '''Generates list of dicts of all players with membersip id, profile and clan name currently in Clan corresponding with clan id'''
            list_of_clan_members = []
            resolved = []
            site_call = "https://www.bungie.net/Platform/GroupV2/" + str(clan[0]) + "/Members/?currentPage=1"
            request = requests.get(site_call, headers={"X-API-Key":self.api_key})
            clan_request_list = request.json()['Response']['results']
            del self.retrys[:] #Empty list
            for val in clan_request_list:
                profile = self.get_DestinyUserProfile(val["destinyUserInfo"]["membershipId"])
                if profile:
                    name = profile["profile"]["data"]["userInfo"]["displayName"]
                    membership_id = profile["profile"]["data"]["userInfo"]["membershipId"]

                    if "bungieNetUserInfo" in val:
                        bungie_id = val["bungieNetUserInfo"]["membershipId"]
                        bungie_profile = self.get_battleTag_from_bungieNetUser(bungie_id)
                        if bungie_profile:
                            battletag = bungie_profile["bungieNetUser"]["blizzardDisplayName"]
                        else:
                            print("bungie_profile ERROR!! no response from get_battleTag_from_bungieNetUser "+name)
                            bungie_id = None
                            bungie_profile = None
                            battletag = name
                    else:
                        #CASOS PROBLEMATICOS
                        #print(val)
                        #print("----------------------------")

                        #bungie_id = "IDBungie_Desconocido"
                        #bungie_profile = "Perfil_Bungie_Desconocido"
                        #battletag = "battletag_desconocido"
                        bungie_id = None
                        bungie_profile = None
                        battletag = name
                        #print(membership_id ,name, profile, clan[1], bungie_id, battletag)
                        #print("----------------------------")
                        #print("\n")
                    
                    player_dict = { membership_id: [name, profile, clan[1], bungie_id, battletag] }
                    list_of_clan_members.append(player_dict)
            while self.retrys:
                #print "RETIES NOT EMPTY !!"
                for val in self.retrys:
                    profile = self.get_DestinyUserProfile(val)
                    if profile:
                        name = profile["profile"]["data"]["userInfo"]["displayName"]
                        membership_id = profile["profile"]["data"]["userInfo"]["membershipId"]
                        if "bungieNetUserInfo" in val:
                            bungie_id = val["bungieNetUserInfo"]["membershipId"]
                            bungie_profile = self.get_battleTag_from_bungieNetUser(bungie_id)
                            if bungie_profile:
                                battletag = bungie_profile["bungieNetUser"]["blizzardDisplayName"]
                            else:
                                print("bungie_profile Rety ERROR!! no response from get_battleTag_from_bungieNetUser"+val)
                                bungie_id = None
                                bungie_profile = None
                                battletag = name
                        else:
                            #bungie_id = "IDBungie_Desconocido"
                            #bungie_profile = "Perfil_Bungie_Desconocido"
                            #battletag = "battletag_desconocido"
                            bungie_id = None
                            bungie_profile = None
                            battletag = name
                        player_dict = { membership_id: [name, profile, clan[1], bungie_id, battletag] }
                        
                        print ("Retrying:"+name+" "+clan[1]+" !!!")
                        player_dict = { membership_id: [name, profile, clan[1], bungie_id, battletag] }
                        list_of_clan_members.append(player_dict)
                        resolved.append(profile["profile"]["data"]["userInfo"]["displayName"])
                        self.retrys.remove(membership_id)
            #await asyncio.sleep(0.01)
            return list_of_clan_members


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


    def push_blacklister_to_db(self, record, blacklisters):
        blacklisters.insert_one(record)


    def push_clanmate_to_db(self, record, clanmates):
        clanmates.insert_one(record)


    def clean_blacklist(self):
            '''Removes blacklisted players based on a whitelist file'''
            with open(my_whitelist_file) as f:
                lines = f.read().splitlines()
            for white in lines:
                for player in self.blacklist:
                    for key in player:
                        if player[key][0] == white:
                            self.blacklist.remove(player)

    
    def upload_blacklist(self):
        #4 tests
        #with open(my_config_file, 'r') as f:
        #    config = json.load(f)
        #MONGODB_URI = config['DEFAULT']['MONGO_DB_MLAB']
        #END tests
        #4 Heroku
        MONGODB_URI = os.environ['MONGO_DB_MLAB']
        #END Heroku
        client = MongoClient(MONGODB_URI, connectTimeoutMS=30000)
        db = client.get_database("bot_definitivo")
        blacklisters = db.blacklist
        #removes all documents from blacklisters
        blacklisters.remove({})
        #Cleans local blacklist with static whitelist file
        self.clean_blacklist()
        for blacklister in self.blacklist:
            my_dict={}
            date=datetime.today().strftime('%Y-%m-%d')
            for key in blacklister:
                my_dict={"displayName":str(blacklister[key][0]), "clan":str(blacklister[key][2]) , "inactive_time":str(blacklister[key][5]),"date":date}
                self.push_blacklister_to_db(my_dict, blacklisters)
    

    def upload_clanmates(self, full_clan_list):
        #4 tests
        #with open(my_config_file, 'r') as f:
        #    config = json.load(f)
        #MONGODB_URI = config['DEFAULT']['MONGO_DB_MLAB']
        #END tests
        #4 Heroku
        MONGODB_URI = os.environ['MONGO_DB_MLAB']
        #END Heroku
        client = MongoClient(MONGODB_URI, connectTimeoutMS=30000)
        db = client.get_database("bot_definitivo")
        clanmates = db.clan_members
        #removes all documents from clan_members
        clanmates.remove({})
        for clanmate in full_clan_list:
            clanmate_dict = {}
            for key in clanmate:
                if key:
                    clanmate_dict = {"battletag":clanmate[key][4] , "clan": clanmate[key][2], "displayName":clanmate[key][0]}
                    self.push_clanmate_to_db(clanmate_dict,clanmates)

    
    def create_blacklist(self):
            '''Generates a list of  blacklisted players'''
            full_clan_list=[]
            for clan in self.our_clans:
                print("Starting SYNC with "+clan[1])
                clan_list = self.get_ClanPlayerList(clan)
                full_clan_list = full_clan_list + clan_list
                print("Searching for blacklisters in "+clan[1]+" ... ")
                for player in clan_list:
                    if self.is_blacklisted(player):
                        self.blacklist.append(player)
                
                print("Uploading blacklisters for "+clan[1])
                self.upload_blacklist()
            print("Uploading Full Clan List")
            self.upload_clanmates(full_clan_list)
            print("Finished SYNC!!")


    def print_blacklist_basic(self):
            '''Prints the list of blacklisted players to stdo'''
            str_list = ""
            for player in self.blacklist:
                for key in player:
                    #print (player[key][0] + "\t" + player[key][2] + "\t" + str(player[key][3])+ "\n")
                    #str_list = str_list + player[key][0] + "\t" + player[key][2] + "\t" + str(player[key][4]) + "\t" + str(player[key][5]) +"\n"
                    str_list = str_list + player[key][0] + "," + player[key][2] + "," + str(player[key][5]) +"\n"
            return str_list
    

    def print_clan_basic(self, clan_list):
            '''Prints the list of Clanmembers to stdo'''
            str_list = ""
            for player in clan_list:
                for key in player:
                    #print (player[key][0] + "\t" + player[key][2] + "\t" + str(player[key][3])+ "\n")
                    str_list = str_list + player[key][0] + "\t" + player[key][2] + "\t" + str(player[key][3])+ "\n"
            return str_list


    def print_blacklist_file(self):
            '''Prints the list of blacklisted players to file'''
            f = open(my_inactive_file, "w")
            for player in self.blacklist:
                for key in player:
                    print(player[key][0] + "\s" + player[key][2] + "\s" + str(player[key][4]) + "\s" + str(player[key][5]) +"\s")
                    f.write(player[key][0] + "\t" + player[key][2] + "\t" + str(player[key][4]) + "\t" + str(player[key][5]) +"\n")
            f.close()
    
    
    def print_clan_2_file(self, full_clan_list):
            '''Prints the list of Clanmates to file'''
            #with open(my_clan_file, 'r') as f:
            #    clanmates = json.load(f)
            aux_dict={}
            for player in full_clan_list:
                #print(player)
                for key in player:
                    if key:
                        aux_dict[player[key][4]] = [player[key][2], player[key][0]]
                    else:
                        print("ERROR writing clanmate to file:  "+player)
                        aux_dict[player[key][0]] = [player[key][2], player[key][0]]
            with open(my_clan_file, 'w') as f:
                    json.dump(aux_dict, f, indent=4)

    ############################################## ASYNC PART ###############################################################
    #########################################################################################################################

    async def async_get_ClanPlayerList(self, clan):
        '''Generates list of dicts of all players with membersip id, profile and clan name currently in Clan corresponding with clan id'''
        temp_list = []
        site_call = "https://www.bungie.net/Platform/GroupV2/" + str(clan[0]) + "/Members/?currentPage=1"
        #request = requests.get(site_call, headers={"X-API-Key":self.api_key})
        headers={"X-API-Key":self.api_key}
        async with aiohttp.get(site_call,headers=headers) as request:
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


    async def async_get_Clanmate_LastPlayed(self, clanmember_membership_id):
        site_call = "https://bungie.net/Platform/Destiny2/4/Profile/" +clanmember_membership_id+ "/" + "?components=100,200"
        headers={"X-API-Key":self.api_key}
        #jar = aiohttp.CookieJar(unsafe=True)
        #async with aiohttp.ClientSession(cookie_jar=jar) as s:
        async with aiohttp.get(site_call,headers=headers) as request:
            if request.status == 200:
                try:
                    json = await request.json()
                    if json['Response']['profile']['data']['dateLastPlayed']:
                            return json['Response']['profile']['data']['dateLastPlayed']
                    else:
                        print("RETRY: Response 200 but no data")
                        return None
                except Exception as ex:
                    print("Console Player:"+clanmember_membership_id)
                    return None
                
                
    async def async_add_Clanmembers_LastPlayed(self, clan_list):
        for clanmember in clan_list:
            await asyncio.sleep(1)
            last_played = await self.async_get_Clanmate_LastPlayed(clanmember["membershipId"])
            if last_played:
                clanmember["platform"] = "PC"
                clanmember["last_played"] = last_played
            else:
                clanmember["platform"] = "Console"
                clanmember["last_played"] = None
        return clan_list


    async def async_get_Clanmate_ClanName(self, clanmember_membership_id):
        '''Gets the players clan name'''
        site_call = "https://www.bungie.net/Platform/GroupV2/User/4/{}/0/1/".format(str(clanmember_membership_id))
        headers={"X-API-Key":self.api_key}
        async with aiohttp.get(site_call,headers=headers) as request:
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
        async with aiohttp.get(site_call,headers=headers) as request:
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
            break_point_seconds=2592000
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
                #print "NOT Blacklisted"
                return None
        else:
            return None


    async def async_filter_blacklist(self, player_list):
        '''Filters special players from blacklist'''
        #4 tests
        #with open(my_config_file, 'r') as f:
        #    config = json.load(f)
        #MONGODB_URI = config['DEFAULT']['MONGO_DB_MLAB']
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
        #MONGODB_URI = config['DEFAULT']['MONGO_DB_MLAB']
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
        #MONGODB_URI = config['DEFAULT']['MONGO_DB_MLAB']
        #END tests
        #4 Heroku
        MONGODB_URI = os.environ['MONGO_DB_MLAB']
        #END Heroku
        client = MongoClient(MONGODB_URI, connectTimeoutMS=30000)
        db = client.get_database("bot_definitivo")
        clanmates = db.clan_members

        clanmates.insert_many(clan_list, ordered=False)


    async def async_clear_clanmates_blacklister_db(self):
        '''Pushes clanmates to db'''
        print("Clearing Blacklist and Clanmates ...")
        #4 tests
        #with open(my_config_file, 'r') as f:
        #    config = json.load(f)
        #MONGODB_URI = config['DEFAULT']['MONGO_DB_MLAB']
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