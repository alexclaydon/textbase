from newspaper import Article
from queue import Queue

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from elasticsearch import Elasticsearch
from elasticsearch_dsl.connections import connections

from textbase.classes_pg import DBArticle
from textbase.classes_es import ESArticle

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


def get_existing_articles_from_es():
    pass


def get_existing_articles_from_pg():
    pass


def dedupe_sets(new_link_set: set, existing_link_set: set):
    return new_link_set.difference(existing_link_set)


def _return_article_from_queue(link_queue: Queue):
    url = link_queue.get()
    # if _check_url_exist(url):
    #     return None
    article = Article(url, keep_article_html=True)
    article.download()
    article.parse()
    article.nlp()
    return article


#TODO: More advanced error handling for _return_article_from_queue(); namely, should keep and present to the user a list of failed downloads generally, and keep an ignore list of 404 failures specifically.


# def _check_url_exist(url):
#     q = session.query(DBArticle).filter(
#         DBArticle.url == url)
#     for item in session.query(q.exists()):
#         if 'True' in str(item):
#             return True


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


def add_article_to_es(link_queue: Queue):
    article = _return_article_from_queue(link_queue)
    if article is not None:
        esarticle = ESArticle(
            # meta={'id': 42},
            url=article.url,
            title=article.title,
            authors=str(article.authors),
            body=article.text,
            # tags=['test'],
        )
        # esarticle.published_from = datetime.now()
        esarticle.save()
