from elasticsearch import Elasticsearch
from elasticsearch_dsl import Document, Integer, Keyword, Text

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
