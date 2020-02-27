#!/usr/bin/env python3

import sys,os
import curses
from pocket_service import get_pocket_instance, fetch_all_items
from urllib import request

def get_text_from_url(url):
    response = request.urlopen(request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})) 
    return response.read()[:500]

def pad_text(string, pad_before=0, pad_after=0, total_length=-1):
    if pad_before > 0:
        string = (" " * pad_before) + string
    if pad_after > 0:
        string = string + (" " * pad_after)
    if total_length > 0:
        string = (string + (" " * 1000))[:total_length]
    return string

def render_item_panel(panel, items, selected_item_index):
    panel.clear()
    height, width = panel.getmaxyx()
    for y in range(0,49):
        if y == selected_item_index:
            panel.attron(curses.color_pair(3))
        panel.addstr(2*y+1,3, pad_text(items[y]['resolved_title'], total_length=47))
        panel.addstr(2*y+2,3, pad_text(items[y]['excerpt'], pad_before=4, total_length=47))
        if y == selected_item_index:
            panel.attroff(curses.color_pair(3))
    panel.border()

def wrap_text(text, line_width):
    lines = []
    while len(text) > 0:
        lines.append(text[:line_width])
        text = text[line_width:]
    return "\n".join(lines)


def render_reading_panel(panel, text):
    panel.clear()
    height, width = panel.getmaxyx()
    #panel.addstr(wrap_text(text, width - 10))
    panel.addstr(text)
    panel.border()


def draw_menu(stdscr):
    k = 0
    height, width = stdscr.getmaxyx()

    pocket_items = fetch_all_items(get_pocket_instance())

    # Clear and refresh the screen for a blank canvas
    stdscr.clear()
    stdscr.refresh()

    item_panel_width = 50
    reading_panel_width = width - 50

    item_panel = curses.newpad(1000,item_panel_width)
    selected_item_index = 0

    reading_panel = curses.newpad(2000,reading_panel_width)

    # Start colors in curses
    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)

    # Loop where k is the last character pressed
    while (k != ord('q')):

        # Initialization
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        if k == curses.KEY_DOWN:
            selected_item_index += 1
        elif k == curses.KEY_UP:
            selected_item_index = max(0, selected_item_index-1)

        # Declaration of strings
        title = "Curses example"[:width-1]
        subtitle = "Written by Clay McLeod"[:width-1]
        keystr = "Last key pressed: {}".format(k)[:width-1]
        statusbarstr = "Press 'q' to exit"
        if k == 0:
            keystr = "No key press detected..."[:width-1]

        # Centering calculations
        start_x_title = int((width // 2) - (len(title) // 2) - len(title) % 2)
        start_x_subtitle = int((width // 2) - (len(subtitle) // 2) - len(subtitle) % 2)
        start_x_keystr = int((width // 2) - (len(keystr) // 2) - len(keystr) % 2)
        start_y = int((height // 2) - 2)

        # Rendering some text
        whstr = "Width: {}, Height: {}".format(width, height)
        stdscr.addstr(0, 0, whstr, curses.color_pair(1))

        # Render status bar
        stdscr.attron(curses.color_pair(3))
        stdscr.addstr(height-1, 0, statusbarstr)
        stdscr.addstr(height-1, len(statusbarstr), " " * (width - len(statusbarstr) - 1))
        stdscr.attroff(curses.color_pair(3))

        # Turning on attributes for title
        stdscr.attron(curses.color_pair(2))
        stdscr.attron(curses.A_BOLD)

        # Rendering title
        stdscr.addstr(start_y, start_x_title, title)

        # Turning off attributes for title
        stdscr.attroff(curses.color_pair(2))
        stdscr.attroff(curses.A_BOLD)

        # Print rest of text
        stdscr.addstr(start_y + 1, start_x_subtitle, subtitle)
        stdscr.addstr(start_y + 3, (width // 2) - 2, '-' * 4)
        stdscr.addstr(start_y + 5, start_x_keystr, keystr)

        # Refresh the screen
        stdscr.refresh()


        render_item_panel(item_panel, pocket_items, selected_item_index)
        # (0,0) : coordinate of upper-left corner of pad area to display.
        # (5,5) : coordinate of upper-left corner of window area to be filled
        #         with pad content.
        # (20, 75) : coordinate of lower-right corner of window area to be
        #          : filled with pad content.
        item_panel.refresh( 0,0, 1,0, height-3,item_panel_width)

        render_reading_panel(reading_panel, get_text_from_url('https://slatestarcodex.com'))
        reading_panel.refresh( 0,0, 1,item_panel_width, height-3,width-1)

        # Wait for next input
        k = stdscr.getch()

def main():
    curses.wrapper(draw_menu)

if __name__ == "__main__":
    main()
