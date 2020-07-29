from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Document, Integer, Keyword, Text
from elasticsearch_dsl.response import Response
from elasticsearch.exceptions import NotFoundError
import pprint

from elasticsearch_dsl.connections import connections

connections.create_connection(hosts=['192.168.2.100'])

# Using ```connections.create_connection``` instead of ```es = Elasticsearch ...``` has one big advantage: namely that when you are interacting with the ES instance using the class defined here (ESArticle, itself subclassed from Document), it will know where to look for the connection in the environment; if you use the other approach instead then, for example, when you try to return an ESArticle using the ESArticle.get() method it will throw a "KeyError: "There is no connection with alias 'default'."

es = Elasticsearch(hosts='192.168.2.100')

pp = pprint.PrettyPrinter(indent=4)

# Define a subclass based on elasticsearch.Document

class ESArticle(Document):
    """
    Based on the example class set out [here](https://pypi.org/project/elasticsearch-dsl/)
    """
    url = Text()
    title = Text(analyzer='snowball', fields={'raw': Keyword()})
    authors = Text()
    body = Text(analyzer='snowball')
    lines = Integer()

    class Index:
        name = 'articles'
        settings = {
            "number_of_shards": 2,
        }

    def save(self, ** kwargs):
        self.lines = len(self.body.split())
        return super(ESArticle, self).save(** kwargs)


# def get_all_existing_articles_from_es(connection=es):
#     res = connection.search(index="articles", body={"query": {"match_all": {}}})
#     results = set()
#     for hit in res['hits']['hits']:
#         results.add(hit['_source']['url'])
#     return results


def new_get_all_existing_urls_from_es():
    return set(
        [item['url'] for item in Search(
            using=es,
            index="articles"
        ).scan()]
    )


def search_existing_articles_by_text(
        text: str,
        connection=es
):
    s = Search(
        using=connection,
        index="articles"
    ).query(
        "match",
        body=text
    )
    return s.execute()


def search_existing_articles_by_url(
        url: str,
        connection=es
):
    s = Search(
        using=connection,
        index="articles"
    ).query(
        "match",
        url=url
    )
    return s.execute()


def search_existing_articles_by_authors(
        authors: str,
        connection=es
):
    s = Search(
        using=connection,
        index="articles"
    ).query(
        "match",
        authors=authors
    )
    return s.execute()


def search_existing_articles_by_title(
        title: str,
        connection=es
):
    s = Search(
        using=connection,
        index="articles").query(
        "match", title=title
    )
    return s.execute()


def pp_search_result(result: Response):
    for hit in result:
        pp.pprint(
            [
                hit.meta.score,
                hit.meta.id,
                hit.title,
                hit.url
            ]
        )


def pp_top_search_result_detailed(result: Response):
    hit = result.hits[0]
    pp.pprint(
        [
            f'Score: {hit.meta.score}',
            f'ID: {hit.meta.id}',
            f'Title: {hit.title}',
            f'Authors: {hit.authors}',
            f'URL: {hit.url}',
            f'Body: {hit.body}',
        ]
    )


def delete_all_articles():
    es.delete_by_query(
        index='articles',
        body={
            "query": {
                "match_all": {}
            }
        }
    )


def return_article_by_id(id):
    try:
        return es.get(index='articles', id=id)
    except NotFoundError:
        print(f'Article with ID {id} not found')


def retrieve_article_as_object_by_id(id):
    article = ESArticle.get(id=id)
    return article


def delete_article_by_id(id: str):
    es.delete(index='articles', id=id)


#### Scratchpad #####

# Search all articles directly using the API
#
# res = es.search(index="articles", body={"query": {"match_all": {}}})
#
# print("Got %d Hits:" % res['hits']['total']['value'])
# for hit in res['hits']['hits']:
#     print("%(title)s %(authors)s %(url)s" % hit["_source"])
#
