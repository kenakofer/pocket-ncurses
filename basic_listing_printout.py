#!/usr/bin/env python3
from readabilipy import *

from pocket import Pocket
from sys import exit
from time import sleep
from configparser import ConfigParser

config_file = "config.ini"

config = ConfigParser()
config.read(config_file)

ITEM_UNARCHIVED = "0"
ITEM_ARCHIVED = "1"

REDIRECT_URI = "https://getpocket.com"
CONSUMER_KEY = config.get("main", "consumer_key")

def get_access_token():
    print("Fetching request token from pocket...")
    request_token = Pocket.get_request_token(consumer_key=CONSUMER_KEY, redirect_uri=REDIRECT_URI)

    # URL to redirect user to, to authorize your app
    auth_url = Pocket.get_auth_url(code=request_token, redirect_uri=REDIRECT_URI)

    user_credentials = None
    while user_credentials == None:
        try:
            print("Trying to get access token from pocket...")
            user_credentials = Pocket.get_credentials(consumer_key=CONSUMER_KEY, code=request_token)
        except Exception as e:
            print(e)
            print("In order to get an access token, you must visit this url to authenticate:",auth_url)
            print("Press enter after giving permission in your browser")
    print("Got an access token")
    return user_credentials['access_token']

def fetch_all_items(pocket_instance):
    return pocket_instance.get(state=0)[0]['list']

def save_access_token(config, token):
    config.set('main', 'access_token', token)
    with open(config_file, 'w') as f:
        config.write(f)
    print("Saved the access token to", config_file)

def fetch_all_items():
    dictionary = pocket_instance.get(state="all")[0]['list']
    return [{**v, 'id': k} for k,v in dictionary.items()]


def filter_items_with_status(all_items, status):
    return filter(lambda item: item['status'] == status, all_items)

access_token = None
if 'access_token' in config.options('main'):
    print("Using the access token stored in", config_file)
    access_token = config.get('main', 'access_token')
else:
    save_access_token(config, get_access_token())

pocket_instance = Pocket(CONSUMER_KEY, access_token)
print("Authentication was successful!")

for item in fetch_all_items():
    if item['is_article']:
        if item['status'] == ITEM_ARCHIVED:
            print("  ARCHIVED", item['id'], item['resolved_title'] or item['given_title'] or "[NO TITLE]")
        else:
            print(item['id'], item['status'], item['resolved_title'] or item['given_title'] or "[NOTITLE]")

# Run this in a python3 repl to mess around with it:
# exec(open("hello_world.py").read())

