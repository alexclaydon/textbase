from textbase.article_writer import dedupe_sets


new_links = set()
new_links.add('asdf')
new_links.add('sdfg')
new_links.add('dfgh')

existing_links = set()
existing_links.add('asdf')


def test_dedupe_sets():
    assert 'asdf' not in dedupe_sets(new_links, existing_links)
