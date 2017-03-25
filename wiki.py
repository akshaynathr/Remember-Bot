from wikiapi import WikiApi
wiki=WikiApi()

def search_wiki(query):
    results=wiki.find(query)

    return results

def get_results_wiki(article):
    article=wiki.get_article(article)
    return article
