from clii import App, Arg
import typing
from elasticsearch_dsl import Search
from elasticsearch import Elasticsearch


es = Elasticsearch(hosts='192.168.2.100')
cli = App()


@cli.cmd
def get_all_existing_articles_from_es(connection=es):
    res = connection.search(index="articles", body={"query": {"match_all": {}}})
    results = set()
    for hit in res['hits']['hits']:
        results.add(hit['_source']['url'])
    return results


@cli.cmd
def search_existing_articles_for_text(text: str, connection=es):
    s = Search(using=connection, index="articles").query("match", body=text)
    response = s.execute()
    for hit in response:
        print(hit.meta.score, hit.title, hit.url)


if __name__ == '__main__':
    cli.run()
