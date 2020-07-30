# TODO: Currently contains the main() function for running the pipeline as a script; in due course to be refactored into a CLI.

import os
from pathlib import Path
import nltk
from queue import Queue
import yaml
from apscheduler.schedulers.blocking import BlockingScheduler


from textbase.setup import setup_dirs, download_nltk_corpora
from textbase.functions import dedupe_sets, write_iterable_to_file
from textbase.api.instapaper import export_link_list_from_instapaper
from textbase.api.todoist import export_link_list_from_todoist
from textbase.api.pg_api import get_all_existing_articles_from_pg
from textbase.api.es_api import new_get_all_existing_urls_from_es, search_existing_articles_by_text
from textbase.url_processor import add_instapaper_urls_to_set_object
from textbase.article_writer import add_article_to_db, add_article_to_es

# Debug flag for modifying program behaviour

if os.getenv("TEXTBASE_DEBUG_MODE"):
    DEBUG_MODE = os.getenv("TEXTBASE_DEBUG_MODE")
else:
    DEBUG_MODE = True

# Paths and files

CONFIG_FILE = Path.cwd() / 'textbase' / 'config.yml'

with open(file=CONFIG_FILE.as_posix(), mode='r') as f:
    config = yaml.safe_load(f)

RESOURCES_PATH = Path.cwd() / 'textbase' / 'resources'

DB_PATH = RESOURCES_PATH / 'db'
LOGS_PATH = RESOURCES_PATH / 'logs'
EXPORT_PATH = RESOURCES_PATH / 'source'
NLTK_CORPUS_PATH = RESOURCES_PATH / 'nltk_data'
nltk.data.path.append(NLTK_CORPUS_PATH.as_posix())

IGNORE_LINKS_FILE = EXPORT_PATH / 'ignore-links.txt'
TODOIST_EXPORT_FILE = EXPORT_PATH / 'todoist-export.md'
INSTAPAPER_EXPORT_FILE = EXPORT_PATH / 'instapaper-export.html'
SAFARI_EXPORT_FILE = EXPORT_PATH / 'Bookmarks.plist'

with open(file=IGNORE_LINKS_FILE.as_posix(), mode='r') as file:
    ignore_link_set = set(file.read().splitlines())

# Tokens

TODOIST_TOKEN = os.getenv("TODOIST_TOKEN")


class Textbase:

    @staticmethod
    def run():
        Textbase.get_article_updates()
        scheduler = BlockingScheduler()
        scheduler.add_job(
            Textbase.get_article_updates,
            'interval',
            hours=12
        )
        scheduler.start()


    @staticmethod
    def get_article_updates():
        for file in EXPORT_PATH.iterdir():
            if file.is_file() and 'insta' in file.as_posix():
                file.unlink()
        setup_dirs([DB_PATH, LOGS_PATH, EXPORT_PATH])
        if not NLTK_CORPUS_PATH.exists():
            download_nltk_corpora(NLTK_CORPUS_PATH)
        if not Path.exists(TODOIST_EXPORT_FILE):
            Path.touch(TODOIST_EXPORT_FILE)
        # export_link_list_from_safari()
        export_link_list_from_instapaper(
            instapaper_login=config['instapaper'],
            firefox_dl_dir=EXPORT_PATH,
            target=INSTAPAPER_EXPORT_FILE
        )
        export_link_list_from_todoist(
            todoist_token=TODOIST_TOKEN,
            target=TODOIST_EXPORT_FILE
        )
        link_set = set()
        # add_safari_urls_to_set_object(
        #     bookmarks_file=SAFARI_EXPORT_FILE,
        #     set_object=link_set
        # )
        add_instapaper_urls_to_set_object(
            html_file=INSTAPAPER_EXPORT_FILE,
            set_object=link_set
        )
        # add_todoist_urls_to_set_object(
        #     md_file=TODOIST_EXPORT_FILE,
        #     set_object=link_set
        # )
        link_queue = Queue()
        if config['output'] == 'es':
            existing_links = new_get_all_existing_urls_from_es()
            for item in dedupe_sets(
                    new_set=link_set,
                    existing_set=existing_links.union(ignore_link_set)
            ):
                link_queue.put(item=item)
            while not link_queue.empty():
                ignore_link_set.add(
                    add_article_to_es(
                        link_queue=link_queue
                    )
                )
        else:
            existing_links = get_all_existing_articles_from_pg()
            for item in dedupe_sets(
                    new_set=link_set,
                    existing_set=existing_links
            ):
                link_queue.put(item=item)
            while not link_queue.empty():
                add_article_to_db(link_queue=link_queue)
        write_iterable_to_file(ignore_link_set, IGNORE_LINKS_FILE)
