#!/usr/bin/env python3

from os import remove, makedirs
import curses
from pocket_service import get_pocket_instance, fetch_all_items
from urllib import request
from readabilipy.readabilipy import simple_json_from_html_string
from ast import literal_eval

result_cache_folder = '.cache/urls/'
makedirs('.cache/urls/', exist_ok=True)

def url_to_cache(url):
    return result_cache_folder + '-'.join(url.replace('https://', '').replace('http://', '').split('/')).strip('-')

def load_cached_result(url):
    try:
        with open(url_to_cache(url), 'r') as f:
            return literal_eval(f.read())
    except:
        return None

def save_cached_result(result, url):
    with open(url_to_cache(url), 'w') as f:
        f.write(str(result))

def remove_cached_url(url):
    remove(url_to_cache(url))

def get_paragraphs_from_url(url, stdscr):
    result = load_cached_result(url)
    if result == None:
        set_status_text(stdscr, 'Fetching '+url+'...')
        response = request.urlopen(request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})).read()
        set_status_text(stdscr, 'Converting '+url+'...')
        json = simple_json_from_html_string(response, use_readability=True)
        result = [d['text'] for d in json["plain_text"]]
        save_cached_result(result, url)
    set_status_text(stdscr, 'Successfully loaded '+url+'.')
    return result

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
    while len(text) > line_width:
        try:
            space_index = text[:line_width].rindex(' ')
            yield text[:space_index]
            text = text[space_index+1:]
        except:
            yield text[:line_width]
            text = text[line_width:]
    yield text

def convert_text_for_display(text):
    return text.strip().replace('\\n', '').replace('\\t', '').replace('\n', '').replace('\\xe2\\x80\\x99', "'")

def render_reading_panel(panel, paragraphs):
    panel.clear()
    height, width = panel.getmaxyx()
    # panel.addstr(str(paragraphs))
    # return
    padding = 2
    y = 1
    for p in paragraphs[:100]:
        block = convert_text_for_display(p)
        for line in wrap_text(block, width - 2*padding):
            panel.addstr(y, padding, line)
            y+=1
    panel.border()

def set_status_text(stdscr, text):
    height, width = stdscr.getmaxyx()
    stdscr.addstr(height-1, 0, pad_text(text, total_length=width-1), curses.A_REVERSE)
    stdscr.refresh()

def draw_menu(stdscr):
    k = 0
    height, width = stdscr.getmaxyx()

    set_status_text(stdscr, 'Logging into pocket...')
    pocket_instance = get_pocket_instance()
    set_status_text(stdscr, 'Loading your listing...')
    pocket_items = fetch_all_items(pocket_instance)
    set_status_text(stdscr, 'Done.')

    # Clear and refresh the screen for a blank canvas
    stdscr.clear()
    stdscr.refresh()

    item_panel_width = 50
    reading_panel_width = min(width - item_panel_width, 150)

    item_panel = curses.newpad(1000,item_panel_width)
    selected_item_index = 0

    reading_panel = curses.newpad(2000,reading_panel_width)

    status_panel_width = width
    status_panel = curses.newpad(1,status_panel_width)

    # Start colors in curses
    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)

    top_reader_line = 0

    reader_panel_needs_refresh = True
    item_panel_needs_render = True
    reader_panel_needs_render = True

    # Loop where k is the last character pressed
    while (k != ord('q')):
        height, width = stdscr.getmaxyx()

        # Move up and down in item list
        if k == ord('J'):
            selected_item_index += 1
            reader_panel_needs_render = True
            item_panel_needs_render = True
            top_reader_line = 0
        elif k == ord('K'):
            selected_item_index = max(0, selected_item_index-1)
            reader_panel_needs_render = True
            item_panel_needs_render = True
            top_reader_line = 0

        # Move up and down in reader panel
        elif k == curses.KEY_DOWN or k == ord('j'):
            top_reader_line += 1
            reader_panel_needs_refresh = True
        elif k == curses.KEY_UP or k == ord('k'):
            top_reader_line = max(0, top_reader_line-1)
            reader_panel_needs_refresh = True

        # Force a refresh of the article that skips the cache
        elif k == ord('R'):
            remove_cached_url(url)
            reader_panel_needs_render = True

        url = pocket_items[selected_item_index]['resolved_url']

        if item_panel_needs_render:
            render_item_panel(item_panel, pocket_items, selected_item_index)
            item_panel.refresh( 0,0, 1,0, height-3,item_panel_width)

        if reader_panel_needs_render:
            reader_panel_needs_refresh = True
            render_reading_panel(reading_panel, get_paragraphs_from_url(url, stdscr))

        if reader_panel_needs_refresh:
            reading_panel_bounds = [1, item_panel_width, height-3, width-1]
            reading_panel.refresh( top_reader_line,0, reading_panel_bounds[0],reading_panel_bounds[1], reading_panel_bounds[2],reading_panel_bounds[3])

        reader_panel_needs_refresh = False
        item_panel_needs_render = False
        reader_panel_needs_render = False

        # Wait for next input
        k = stdscr.getch()

def main():
    curses.wrapper(draw_menu)

if __name__ == "__main__":
    main()
