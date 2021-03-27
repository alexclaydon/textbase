import os
from pathlib import Path
import nltk
from queue import Queue
import yaml
from apscheduler.schedulers.blocking import BlockingScheduler

from .api.legacy import local_logger
from newspaper import Article
from newspaper.article import ArticleException

import datetime

from textbase.setup import setup_dirs, download_nltk_corpora
from textbase.functions import dedupe_sets, write_iterable_to_file
from textbase.api.instapaper import export_link_list_from_instapaper
from textbase.api.todoist import export_link_list_from_todoist
from textbase.api.pg_api import get_all_existing_articles_from_pg
from textbase.api.es_api import new_get_all_existing_urls_from_es, search_existing_articles_by_text
from textbase.url_processor import add_instapaper_urls_to_set_object

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, DateTime, String

# from textbase.api.pg_api import DBArticle
# from textbase.article_writer import add_article_to_db

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
DB_LOCATION = 'sqlite:///' + os.getcwd() + '/textbase/resources/db/articles.db'
LOGS_PATH = RESOURCES_PATH / 'logs'
EXPORT_PATH = RESOURCES_PATH / 'source'
NLTK_CORPUS_PATH = RESOURCES_PATH / 'nltk_data'
nltk.data.path.append(NLTK_CORPUS_PATH.as_posix())

IGNORE_LINKS_FILE = EXPORT_PATH / 'ignore-links.txt'
TODOIST_EXPORT_FILE = EXPORT_PATH / 'todoist-export.md'
INSTAPAPER_EXPORT_FILE = EXPORT_PATH / 'instapaper-export.html'
SAFARI_EXPORT_FILE = EXPORT_PATH / 'Bookmarks.plist'

if IGNORE_LINKS_FILE.exists():
    with open(file=IGNORE_LINKS_FILE.as_posix(), mode='r') as file:
        ignore_link_set = set(file.read().splitlines())
else:
    ignore_link_set = set()
    IGNORE_LINKS_FILE.touch()

# Tokens

TODOIST_TOKEN = os.getenv("TODOIST_TOKEN")

# SQLite database setup

engine = create_engine(DB_LOCATION, connect_args={'check_same_thread': False})
Base = declarative_base()

class DBArticle(Base):
    __tablename__ = 'articles'

    id = Column(Integer(), primary_key=True)
    timestamp = Column(DateTime(), nullable=False)
    url = Column(String(), nullable=False)
    title = Column(String(), nullable=False)
    top_image_url = Column(String(), nullable=False)
    authors = Column(String(), nullable=True)
    text = Column(String(), nullable=False)
    article_html = Column(String(), nullable=False)
    full_html = Column(String(), nullable=False)
    summary = Column(String(), nullable=False)
    keywords = Column(String(), nullable=False)
    all_images_urls = Column(String(), nullable=True)
    movies_urls = Column(String(), nullable=True)

    def __init__(
            self,
            url,
            title,
            top_image_url,
            authors,
            text,
            article_html,
            full_html,
            summary,
            keywords,
            all_images_urls,
            movies_urls,
    ):
        self.timestamp = datetime.datetime.now()
        self.url = url
        self.title = title
        self.top_image_url = top_image_url
        self.authors = authors
        self.text = text
        self.article_html = article_html
        self.full_html = full_html
        self.summary = summary
        self.keywords = keywords
        self.all_images_urls = all_images_urls
        self.movies_urls = movies_urls

    def __repr__(self):
        return f'''Article(id={self.id}, datetime={self.timestamp}, url={self.url}, 
        title={self.title}, top_image_url={self.top_image_url}, authors={self.authors}, 
        text={self.text}, article_html={self.article_html}, full_html={self.full_html}, 
        summary={self.summary}, keywords={self.keywords}, 
        all_images_urls={self.all_images_urls}, movies_urls={self.movies_urls})'''

Session = sessionmaker(bind=engine)
session = Session()
Base.metadata.create_all(engine)


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
        setup_dirs([DB_PATH, LOGS_PATH, EXPORT_PATH])
        for file in EXPORT_PATH.iterdir():
            if file.is_file() and 'insta' in file.as_posix():
                file.unlink()
        if not NLTK_CORPUS_PATH.exists():
            download_nltk_corpora(NLTK_CORPUS_PATH)
        # if not Path.exists(TODOIST_EXPORT_FILE):
        #     Path.touch(TODOIST_EXPORT_FILE)
        # export_link_list_from_safari()
        export_link_list_from_instapaper(
            instapaper_login=config['instapaper'],
            firefox_dl_dir=EXPORT_PATH,
            target=INSTAPAPER_EXPORT_FILE
        )
        # export_link_list_from_todoist(
        #     todoist_token=TODOIST_TOKEN,
        #     target=TODOIST_EXPORT_FILE
        # )
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
        # if config['output'] == 'es':
        #     existing_links = new_get_all_existing_urls_from_es()
        #     for item in dedupe_sets(
        #             new_set=link_set,
        #             existing_set=existing_links.union(ignore_link_set)
        #     ):
        #         link_queue.put(item=item)
        #     while not link_queue.empty():
        #         ignore_link_set.add(
        #             add_article_to_es(
        #                 link_queue=link_queue
        #             )
        #         )
        if config['output'] == 'db':
            existing_links = get_all_existing_articles_from_pg()
            for item in dedupe_sets(
                    new_set=link_set,
                    existing_set=existing_links
            ):
                link_queue.put(item=item)
            while not link_queue.empty():
                add_article_to_db(session=session, link_queue=link_queue)
        elif config['output'] != 'db':
            print('Check misconfigured config.yml file')
            exit()
        write_iterable_to_file(ignore_link_set, IGNORE_LINKS_FILE)


def _return_article_from_queue(link_queue: Queue):
    url = link_queue.get()
    article = Article(url, keep_article_html=True)
    try:
        article.download()
        article.parse()
        article.nlp()
    except ArticleException as e:
        local_logger.warning(msg=e)
        return article.url
    return article


def add_article_to_db(session, link_queue: Queue):
    article = _return_article_from_queue(link_queue)
    if isinstance(article, str):
        ignore_link_set.add(article)
    if isinstance(article, Article):
        session.add(
            DBArticle(
                url=article.url,
                title=article.title,
                top_image_url=article.top_image,
                authors=str(article.authors),
                text=article.text,
                article_html=article.article_html,
                full_html=article.html,
                summary=article.summary,
                keywords=str(article.keywords),
                all_images_urls=str(article.images),
                movies_urls=str(article.movies),
            )
        )
        session.commit()
