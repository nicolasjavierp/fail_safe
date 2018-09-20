import requests
import os
from lxml import html
import json


bungie_api_key = os.environ["BUNGIE_API_KEY"]

HEADERS = {"X-API-Key":bungie_api_key}

bungie_request = requests.get("https://www.bungie.net/Platform/Destiny2/SearchDestinyPlayer/4/Javu%232632", headers={"X-API-Key": bungie_api_key })

print int(bungie_request.json()['Response'][0]['membershipId'])