#!/usr/local/bin/python3.6
# -*- coding: utf-8 -*-
from fail_safe import FailSafe
import os
import json
from time import sleep
import asyncio
import aiohttp

THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
my_config_file = os.path.join(THIS_FOLDER, 'config.json')

with open(my_config_file, 'r') as f:
        config = json.load(f)

bungie_api_key = config['DEFAULT']['BUNGIE_API_KEY'] # 'secret-bungie-key-of-fail_safe'

#fs = FailSafe(api_key=os.environ["BUNGIE_API_KEY"]) # Never put your keys in code... export 'em!
fs = FailSafe(api_key=bungie_api_key)
print("Running Blacklist...")
fs.create_blacklist()
#fs.clean_blacklist()
#fs.print_blacklist_file()
#print(fs.print_blacklist_basic())
print("Finnished Blacklist!")