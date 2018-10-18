#!/usr/local/bin/python3.6
# -*- coding: utf-8 -*-
from fail_safe import FailSafe
import os

fs = FailSafe(api_key=os.environ["BUNGIE_API_KEY"]) # Never put your keys in code... export 'em!
fs.create_blacklist()
fs.clean_blacklist()
fs.print_blacklist_file()
