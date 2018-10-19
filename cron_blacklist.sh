#!/usr/bin/env bash

if [[ $(($(date +%W)%2)) -eq 0 ]]; then
  echo "I should be running BlackList"
  /home/njp/Downloads/clan/fail_safe/bot_p3.6/bin/python3.6 /home/njp/Downloads/clan/fail_safe/run_blacklist.py
else
  echo "Not this week dude !"
fi

