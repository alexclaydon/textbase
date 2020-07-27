#### SEARCH #####

from elasticsearch_dsl import Search

#
#
# # Retrieve article as a Python object (using ID)
#
# # article = ESArticle.get(id=42)
# # print(article.title, article.authors)
#
# # Search all articles directly using the API
#
res = es.search(index="articles", body={"query": {"match_all": {}}})
#
print("Got %d Hits:" % res['hits']['total']['value'])
for hit in res['hits']['hits']:
    print("%(title)s %(authors)s %(url)s" % hit["_source"])
#
# # Search for words directly using the API
#
# s = Search(using=es)
# s.query("match", body="culture")
# response = s.execute(ignore_cache=True)
# for hit in response['hits']:
#     print(hit.title)


s = Search(using=es, index="articles").query("match", body="raspberry pi camera")

response = s.execute()

for hit in response:
    print(hit.meta.score, hit.title)
