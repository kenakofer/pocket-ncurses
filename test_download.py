#!/usr/bin/env python3

from urllib import request
from readabilipy.readabilipy import simple_json_from_html_string

def get_text_from_url(url):
    response = request.urlopen(request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})).read()
    json = simple_json_from_html_string(response, use_readability=True)
    return json


if __name__ == "__main__":
    print(get_text_from_url('https://slatestarcodex.com'))
