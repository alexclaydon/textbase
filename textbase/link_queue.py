import plistlib
from queue import Queue
from bs4 import BeautifulSoup


def _gen_constructor_safari_url(bookmarks_file):
    with open(bookmarks_file, 'rb') as file:
        plist = plistlib.load(file)
    children = plist['Children']
    for child in children:
        if child.get('Title', None) == 'com.apple.ReadingList':
            reading_list = child
    bookmarks = reading_list['Children']
    for item in bookmarks:
        yield item['URLString']


def import_safari_links(queue: Queue, bookmarks_file):
    for item in _gen_constructor_safari_url(bookmarks_file):
        queue.put(item)


def _gen_constructor_instapaper_url(html_file):
    with open(html_file, 'r') as file:
        soup = BeautifulSoup(file, features="lxml")
    for link in soup.find_all('a', href=True):
        yield link['href']


def import_instapaper_links(queue: Queue, html_file):
    for item in _gen_constructor_instapaper_url(html_file):
        queue.put(item)


def _gen_constructor_todoist_url():
    pass


def import_todoist_links(queue, markdown_file):
    pass
