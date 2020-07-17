from elasticsearch import Elasticsearch
from elasticsearch_dsl import Document, Date, Integer, Keyword, Text

# Define a custom class based on Document


class ESArticle(Document):
    """
    Based on the example class set out [here](https://pypi.org/project/elasticsearch-dsl/)
    """
    url = Text()
    title = Text(analyzer='snowball', fields={'raw': Keyword()})
    authors = Text()
    body = Text(analyzer='snowball')
    # tags = Keyword()
    # published_from = Date()
    lines = Integer()

    class Index:
        name = 'instapaper-articles'
        # settings = {
        #     "number_of_shards": 1,
        # }

    def save(self, ** kwargs):
        self.lines = len(self.body.split())
        return super(ESArticle, self).save(** kwargs)
    #
    # def is_published(self):
    #     return datetime.now() > self.published_from
