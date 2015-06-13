from collections import defaultdict

from django.db.models.query import QuerySet


def group_connections(connections):
    """
    Return a list of (language code, respective connections) pairs, while
    using Django's translation.override() to set each language.
    """
    grouped_conns = defaultdict(list)
    if isinstance(connections, QuerySet):
        languages = connections.values_list('contact__language', flat=True)
        for language in languages.distinct():
            lang_conns = connections.filter(contact__language=language)
            grouped_conns[language].extend(lang_conns)
    else:
        for connection in connections:
            language = connection.contact.language
            grouped_conns[language].append(connection)
    for lang, conns in grouped_conns.items():
        yield lang, conns
