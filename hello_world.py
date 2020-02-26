#!/usr/bin/env python3
from readabilipy import *

from pocket import Pocket
from sys import exit
from time import sleep
from configparser import ConfigParser

config_file = "config.ini"

config = ConfigParser()
config.read(config_file)

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
            print("You must visit this url to authenticate:",auth_url)
            sleep(1)
    print("Authentication successful:", user_credentials)
    return user_credentials['access_token']

access_token = None
if 'access_token' in config.options('main'):
    access_token = config.get('main', 'access_token')
else:
    access_token = get_access_token()
    config.set('main', 'access_token', access_token)
    with open(config_file, 'w') as f:
        config.write(f)

pocket_instance = Pocket(CONSUMER_KEY, access_token)
# Run this in a python3 repl like:
# exec(open("hello_world.py").read())
