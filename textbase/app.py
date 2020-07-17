# TODO: Currently contains the main() function for running the pipeline as a script; in due course to be refactored into a CLI.

import os
from pathlib import Path
import nltk
from queue import Queue
import yaml

from liblogger.legacy import local_logger

from textbase.setup import setup_dirs, download_nltk_corpora
from textbase.export_instapaper import export_link_list_from_instapaper
from textbase.export_todoist import export_link_list_from_todoist
from textbase.link_queue import import_instapaper_links, import_safari_links, import_todoist_links
from textbase.writer import add_article_to_db, add_article_to_es

# Paths and files

CONFIG_FILE = Path.cwd() / 'textbase' / 'config.yml'

with open(file=CONFIG_FILE.as_posix(), mode='r') as f:
    config = yaml.safe_load(f)

RESOURCES_PATH = Path.cwd() / 'textbase' / 'resources'

DB_PATH = RESOURCES_PATH / 'db'
LOGS_PATH = RESOURCES_PATH / 'logs'
EXPORT_PATH = RESOURCES_PATH / 'source'
NLTK_CORPUS_PATH = RESOURCES_PATH / 'nltk_data'

TODOIST_EXPORT_FILE = EXPORT_PATH / 'todoist-export.md'
INSTAPAPER_EXPORT_FILE = EXPORT_PATH / 'instapaper-export.html'
SAFARI_EXPORT_FILE = EXPORT_PATH / 'Bookmarks.plist'

# Tokens

TODOIST_TOKEN = os.getenv("TODOIST_TOKEN")


class Textbase:

    @staticmethod
    def run():
        # for file in EXPORT_PATH.iterdir():
        #     if file.is_file() and 'insta' in file.as_posix():
        #         file.unlink()

        setup_dirs([DB_PATH, LOGS_PATH, EXPORT_PATH])
        if not NLTK_CORPUS_PATH.exists():
            download_nltk_corpora(NLTK_CORPUS_PATH)
        nltk.data.path.append(NLTK_CORPUS_PATH.as_posix())

        if not Path.exists(TODOIST_EXPORT_FILE):
            Path.touch(TODOIST_EXPORT_FILE)

        export_link_list_from_instapaper(
            instapaper_login=config['instapaper'],
            firefox_dl_dir=EXPORT_PATH,
            target=INSTAPAPER_EXPORT_FILE
        )

        # export_link_list_from_todoist(
        #     todoist_token=TODOIST_TOKEN,
        #     target=TODOIST_EXPORT_FILE
        # )

        link_queue = Queue()
        import_instapaper_links(
            queue=link_queue,
            html_file=INSTAPAPER_EXPORT_FILE
        )
        # import_todoist_links(
        #     queue=link_queue,
        #     markdown_file=TODOIST_EXPORT_FILE
        # )
        # import_safari_links(
        #     queue=link_queue,
        #     bookmarks_file=SAFARI_EXPORT_FILE
        # )

        if config['output'] == 'es':
            while not link_queue.empty():
                add_article_to_es(link_queue=link_queue)
        else:
            while not link_queue.empty():
                add_article_to_db(link_queue=link_queue)
