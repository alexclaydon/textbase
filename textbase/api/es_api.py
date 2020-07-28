from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Document, Integer, Keyword, Text

es = Elasticsearch(hosts='192.168.2.100')

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


def get_all_existing_articles_from_es(connection=es):
    res = connection.search(index="articles", body={"query": {"match_all": {}}})
    results = set()
    for hit in res['hits']['hits']:
        results.add(hit['_source']['url'])
    return results


def new_get_all_existing_urls_from_es():
    return set([item['url'] for item in Search(using=es, index="articles").scan()])


def search_existing_articles_for_text(text: str, connection=es):
    s = Search(using=connection, index="articles").query("match", body=text)
    response = s.execute()
    for hit in response:
        print(hit.meta.score, hit.title, hit.url)


def delete_all_articles():
    es.delete_by_query(index='articles', body={"query": {"match_all": {}}})


#### Scratchpad #####
# 
# Retrieve article as a Python object (using ID)

# article = ESArticle.get(id=42)
# print(article.title, article.authors)

# Search all articles directly using the API
#
# res = es.search(index="articles", body={"query": {"match_all": {}}})
#
# print("Got %d Hits:" % res['hits']['total']['value'])
# for hit in res['hits']['hits']:
#     print("%(title)s %(authors)s %(url)s" % hit["_source"])
#
# # Search for words directly using the API
#
# s = Search(using=es)
# s.query("match", body="culture")
# response = s.execute(ignore_cache=True)
# for hit in response['hits']:
#     print(hit.title)
#
#
# s = Search(using=es, index="articles").query("match", body="raspberry pi camera")
#
# response = s.execute()
#
# for hit in response:
#     print(hit.meta.score, hit.title, hit.url)
