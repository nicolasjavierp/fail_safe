import requests
import os
from lxml import html
import json


bungie_api_key = os.environ["BUNGIE_API_KEY"]

HEADERS = {"X-API-Key":bungie_api_key}

bungie_request = requests.get("https://www.bungie.net/Platform/Destiny2/SearchDestinyPlayer/4/Javu%232632", headers={"X-API-Key": bungie_api_key })

membersip_id = int(bungie_request.json()['Response'][0]['membershipId'])
print membersip_id

bungie_request = requests.get("https://www.bungie.net/Platform/GroupV2/User/4/{}/0/1/".format(membersip_id), headers={"X-API-Key": bungie_api_key })

print bungie_request.json()['Response']['results'][0]['group']['name']