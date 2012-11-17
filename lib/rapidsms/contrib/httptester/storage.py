""" Store and get messages from cache """

from django.core.cache import cache


CACHE_KEY = 'rapidsms-httptester-cache'


def get_messages():
    return cache.get(CACHE_KEY, [])


def store_message(direction, identity, text):
    messages = get_messages()
    data = {"identity": identity, "direction": direction, "text": text}
    messages.append(data)
    cache.set(CACHE_KEY, messages)


def store_and_queue(backend_name, identity, text):
    from rapidsms.router import receive
    store_message('in', identity, text)
    receive(text, backend_name, identity)
