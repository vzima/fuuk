from django import template

register = template.Library()

def citation(article):
    pages = None
    if article.page_from:
        if article.page_to:
            pages = u"%s-%s" % (article.page_from, article.page_to)
        else:
            pages = unicode(article.page_from)

    tag_context = {
        'authors': article.author_set.select_related('person').order_by('order'),
        'identification': article.identification,
        'title': article.title,
        'publication': article.publication,
        'volume': article.volume,
        'place': article.place,
        'year': article.year,
        'pages': pages,
        'type': article.type,
        'presenter': article.presenter,
    }
    return tag_context

register.inclusion_tag('people/citation.html')(citation)