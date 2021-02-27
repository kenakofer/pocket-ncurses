#!/usr/bin/env python3

from pocket_service import *
from datetime import datetime

def main():
    items = fetch_all_items(get_pocket_instance())
    items.sort(key=lambda i: int(i['time_read']))
    for i in items:
        # Skip over non-archived (meaning not read yet) items
        if i['status'] != ITEM_ARCHIVED:
            continue

        time_archived = datetime.fromtimestamp(int(i['time_read']))

        print("TITLE:", i['resolved_title'])
        print("URL:", i['resolved_url'])
        print("READ AT:", time_archived)
        print("EXCERPT:", i['excerpt'])
        print()

if __name__ == "__main__":
    main()
