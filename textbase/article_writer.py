from liblogger.legacy import local_logger
from newspaper import Article
from newspaper.article import ArticleException
from queue import Queue

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from elasticsearch import Elasticsearch
from elasticsearch_dsl.connections import connections

from textbase.api.pg_api import DBArticle
from textbase.api.es_api import ESArticle

# Setup SQLite database connection

Base = declarative_base()
db_location = 'sqlite:///textbase/resources/db/articles.db'
engine = create_engine(db_location, connect_args={'check_same_thread': False})
Session = sessionmaker(bind=engine)
session = Session()

# Initialise class mappings in SQLite database
Base.metadata.create_all(engine)

# Setup Elasticsearch connection
connections.create_connection(hosts=['192.168.2.100'])

es = Elasticsearch(hosts='192.168.2.100')

# Initialise class mappings in Elasticsearch
ESArticle.init()


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


def add_article_to_es(link_queue: Queue):
    article = _return_article_from_queue(link_queue)
    if isinstance(article, Article):
        esarticle = ESArticle(
            url=article.url,
            title=article.title,
            authors=str(article.authors),
            body=article.text,
        )
        esarticle.save()
    if isinstance(article, str):
        return article


def add_article_to_db(link_queue: Queue):
    article = _return_article_from_queue(link_queue)
    if article is not None:
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
