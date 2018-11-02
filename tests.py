#!/usr/local/bin/python3.6
# -*- coding: utf-8 -*-
from fail_safe import FailSafe
import os
from urllib.request import urlopen
import json
import random


fs = FailSafe(api_key=os.environ["BUNGIE_API_KEY"]) # Never put your keys in code... export 'em!
print(fs.get_PlayerClanName("4611686018472677917"))

response = json.loads(urlopen("http://api.giphy.com/v1/gifs/search?q=ryan+gosling&api_key=jhxf3M81M735O3GuMlQmXRtQBJXBXH3Q&limit=5").read())
embed_list = [d['embed_url'] for d in response['data']]

print(random.choice(embed_list))

exit(0)

for key, value in data.items():
    #print(type(value))
    for i in value:
        print(type(i))
        for key, value in value.items():
            print(type(i))
    #print(value['embed_url'])

    
exit(0)
fs.clean_clan_file()
fs.create_blacklist()
fs.clean_blacklist()
fs.print_blacklist_file()


"Javu#2632": [
        "Escuadra 4",
        "Javu"
    ],