import requests
import os
from datetime import datetime
from datetime import timedelta



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
        self.clan_ids = [2943900, 3084439, 3111393, ]

    def get_playerByTagName(self, gamertag):
        '''gamertag (str): The PC gamertag a player uses on Destiny 2'''
        site_call = "https://www.bungie.net/Platform/Destiny2/SearchDestinyPlayer/4/" + gamertag
        request = requests.get(site_call,
                                headers={"X-API-Key":self.api_key})
        return request.json()['Response']

    def get_DestinyUserId(self, gamertag):
        '''gamertag (str): The PC gamertag a player uses on Destiny 2'''
        info = self.get_playerByTagName(gamertag)
        return int(info[0]['membershipId'])

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
        components = "?components=" + ','.join([str(c) for c in components])
        site_call = "https://bungie.net/Platform/Destiny2/4/Profile/" + str(membership_id) + "/" + components
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
            site_call = "https://www.bungie.net/Platform/GroupV2/User/4/{}/0/1/".format(str(membership_id))
            request = requests.get(site_call,
                                    headers={"X-API-Key":self.api_key})
            return request.json()['Response']['results'][0]['group']['name']

    def get_PlayerLastLogin(self, membership_id):
            '''Last time player logged in to Destiny 2'''
            info = self.get_DestinyUserProfile(membership_id)
            return info['profile']['data']['dateLastPlayed']

    def format_PlayerBattleTag(self, battle_tag):
            '''Bungie's api does not undertand the symbol # so you have to encode it like %23
            So Javu#2632 is Javu%232632'''
            return battle_tag.replace('#', '%23')

    def is_blacklisted(self, destiny_id):
            break_point_seconds=1296000
            #test_last_played = datetime.strptime("2018-04-21 07:21:36","%Y-%m-%d %H:%M:%S")
            #print test_last_played
            last_played = datetime.strptime(fs.get_PlayerLastLogin(destiny_id), "%Y-%m-%dT%H:%M:%SZ")
            now = datetime.utcnow().replace(microsecond=0)
            diff = now - last_played
            #test_diff = now - test_last_played
            delta_seconds = diff.total_seconds()
            #delta_test_seconds = test_diff.total_seconds()
            if (delta_seconds > break_point_seconds):
                #print "Blacklisted"
                return True
            else:
                #print "NOT Blacklisted"
                return False
    def get_ClanPlayerList(self, clan_id):
            '''Returns Json of all players currently in Clan corresponding with clan id'''
            list_of_clan_members = []
            site_call = "https://www.bungie.net/Platform/GroupV2/" + str(clan_id) + "/Members/?currentPage=1"
            request = requests.get(site_call,
                                headers={"X-API-Key":self.api_key})
            clan_request_list = request.json()['Response']['results']
            for idx, val in enumerate(clan_request_list):
                player_dict = { val["destinyUserInfo"]["membershipId"]: val["destinyUserInfo"]["displayName"] }
                list_of_clan_members.append(player_dict)
            return list_of_clan_members

    def create_blacklist(self):
            '''Generates a list of  blacklisted players'''
            for id in self.clan_ids:
                clan = self.get_ClanPlayerList(id)
                for player in clan:
                    if self.is_blacklisted(player):
                        self.blacklist.append(player)

            


if __name__ == '__main__':
    fs = FailSafe(api_key=os.environ["BUNGIE_API_KEY"]) # Never put your keys in code... export 'em!

    my_battle_tag="Javu#2632"
    # Get Destiny MembershipId by pc gamertag
    my_destiny_id = fs.get_DestinyUserId(fs.format_PlayerBattleTag(my_battle_tag))
    print("Javu's Destiny ID is: {}".format(my_destiny_id)) 
    # Get User's Profile info and more detailed Character info
    my_profile = fs.get_DestinyUserProfile(my_destiny_id, components=[100,200])
    # Get a random single game's post carnage stats
    #game_stats = fs.get_postGameStats(100)
    #print("Random Destiny 2 game's post carnage game stats: \n{}".format(game_stats))

    # Get players clan
    my_destiny_clan_name = fs.get_PlayerClanName(my_destiny_id)
    print("Destiny player Javu is in: {}".format(my_destiny_clan_name))
    fs.is_blacklisted(my_destiny_id)
    print "CLan_List:"
    print type(fs.get_ClanPlayerList(3111393))
    print fs.get_ClanPlayerList(3111393)