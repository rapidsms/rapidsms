Example use of KeywordHandler::

    #!/usr/bin/env python
    # vim: ai ts=4 sts=4 et sw=4

    from rapidsms.contrib.handlers.handlers.keyword import KeywordHandler

    class EchoHandler(KeywordHandler):
      """
      Handle any message prefixed ECHO, responding with the remainder of
      the text. Useful for remotely checking that the router is running.
      """

      keyword = "ECHO"

      def help(self):
          """ Response to text of the form 'ECHO'"""
          self.respond("To echo some text, send: ECHO <ANYTHING>")
    
      def handle(self, text):
          """ Response to text of the form 'ECHO blargh'"""
          self.respond(text)
