from pathlib import Path
import json
import datetime
import sqlite3
import os

from sqlalchemy import Column, Integer, DateTime, String

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


# class DBArticle(Base):
#     __tablename__ = 'articles'

#     id = Column(Integer(), primary_key=True)
#     timestamp = Column(DateTime(), nullable=False)
#     url = Column(String(), nullable=False)
#     title = Column(String(), nullable=False)
#     top_image_url = Column(String(), nullable=False)
#     authors = Column(String(), nullable=True)
#     text = Column(String(), nullable=False)
#     article_html = Column(String(), nullable=False)
#     full_html = Column(String(), nullable=False)
#     summary = Column(String(), nullable=False)
#     keywords = Column(String(), nullable=False)
#     all_images_urls = Column(String(), nullable=True)
#     movies_urls = Column(String(), nullable=True)

#     def __init__(
#             self,
#             url,
#             title,
#             top_image_url,
#             authors,
#             text,
#             article_html,
#             full_html,
#             summary,
#             keywords,
#             all_images_urls,
#             movies_urls,
#     ):
#         self.timestamp = datetime.datetime.now()
#         self.url = url
#         self.title = title
#         self.top_image_url = top_image_url
#         self.authors = authors
#         self.text = text
#         self.article_html = article_html
#         self.full_html = full_html
#         self.summary = summary
#         self.keywords = keywords
#         self.all_images_urls = all_images_urls
#         self.movies_urls = movies_urls

#     def __repr__(self):
#         return f'''Article(id={self.id}, datetime={self.timestamp}, url={self.url}, 
#         title={self.title}, top_image_url={self.top_image_url}, authors={self.authors}, 
#         text={self.text}, article_html={self.article_html}, full_html={self.full_html}, 
#         summary={self.summary}, keywords={self.keywords}, 
#         all_images_urls={self.all_images_urls}, movies_urls={self.movies_urls})'''


def db():
    return sqlite3.connect(database='resources/db/articles.db')


def query_db(query, args=(), one=False):
    cur = db().cursor()
    cur.execute(query, args)
    r = [dict((cur.description[i][0], value) \
              for i, value in enumerate(row)) for row in cur.fetchall()]
    cur.connection.close()
    return (r[0] if r else None) if one else r


def db_backup(database=os.getcwd() + '/db/articles.db'):
    con = sqlite3.connect(database)
    bck = sqlite3.connect(database.strip('.db') + '_backup.db')
    con.backup(bck)
    bck.close()
    con.close()


# query_all_articles = query_db("select id, timestamp, url, title, text from articles")


def dump_db_to_json(query, target: Path):
    data = json.loads(json.dumps(query))
    with open(target.as_posix(), 'w') as outfile:
        json.dump(data, outfile, indent=4)


def get_all_existing_articles_from_pg():
    """
    In time, to return a list of URLs of all existing articles stored in the database; currently returns an empty dummy list
    """
    return list()


# def _check_url_exist(url):
#     q = session.query(DBArticle).filter(
#         DBArticle.url == url)
#     for item in session.query(q.exists()):
#         if 'True' in str(item):
#             return True
