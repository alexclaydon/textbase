import plistlib
from bs4 import BeautifulSoup


def add_safari_urls_to_set_object(bookmarks_file, set_object: set):
    with open(bookmarks_file, 'rb') as file:
        plist = plistlib.load(file)
    children = plist['Children']
    for child in children:
        if child.get('Title', None) == 'com.apple.ReadingList':
            reading_list = child
    bookmarks = reading_list['Children']
    for item in bookmarks:
        set_object.add(item['URLString'])
    return set_object


def add_instapaper_urls_to_set_object(html_file, set_object: set):
    with open(html_file, 'r') as file:
        soup = BeautifulSoup(file, features="lxml")
    for link in soup.find_all('a', href=True):
        set_object.add(link['href'])
    return set_object


def add_todoist_urls_to_set_object(md_file, set_object: set):
    with open(md_file, 'r') as file:
        soup = BeautifulSoup(file, features="lxml")
    for link in soup.find_all('a', href=True):
        set_object.add(link['href'])
    return set_object


# import markdown
# from lxml import etree
#
# body_markdown = "This is an [inline link](http://google.com). This is a [non inline link][1]\r\n\r\n  [1]: http://yahoo.com"
#
# doc = etree.fromstring(markdown.markdown(body_markdown))
# for link in doc.xpath('//a'):
#     print(link.get('href'))
#
# document = etree.fromstringlist(markdown.markdownFromFile(input=TODOIST_EXPORT_FILE.as_posix()))
#
# markdown.markdownFromFile(input=TODOIST_EXPORT_FILE.as_posix())
#
# qwe = markdown.Markdown()
#
#
# markdown.Markdown.convertFile(input=TODOIST_EXPORT_FILE, output='output.html')
# document = etree.open('output.md')
#
# for link in document.xpath('//a'):
#     print(link.get('href'))
#
#
# with open (TODOIST_EXPORT_FILE, 'rt') as myfile:
#     contents = myfile.readlines()
