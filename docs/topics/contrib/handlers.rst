Code
======

Here is a code example simple keyword handler.
::

    from rapidsms.contrib.handlers.handlers.keyword import KeywordHandler

    class LatrineHandler(KeywordHandler):
        keyword = "latrine"

        def help(self):
            self.respond("Send LATRINE FULL or LATRINE EMPTY.")

        def handle(self, text):
            if text.upper() == "FULL":
                self.respond("Please empty the latrine.")

            elif text.upper() == "EMPTY":
                self.respond("That's great news.")

            else:
                self.help()

Usage
=========

An example of a scripted SMS conversations using this handler include:

The help conversation::

    » latrine
    « Send LATRINE FULL or LATRINE EMPTY.

The conversation stating the latrine is empty::

    » latrine empty
    « That's great news.

The conversation stating the latrine is full::

    » latrine full
    « Please empty the latrine.
