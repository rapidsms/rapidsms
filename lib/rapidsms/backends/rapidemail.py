#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from rapidsms.message import Message
from rapidsms.connection import Connection
import backend
from email import message_from_string

from django.core.mail import *

class Backend(backend.Backend):
    '''Uses the django mail object utilities to send outgoing messages
       via email.  Messages can be formatted in standard smtp, and these
       parameters will end up going into the subject/to/from of the
       email.  E.g.
       ==
       
       Subject: Test message

       Hello Alice.
       This is a test message with 5 header fields and 4 lines in the message body.
       Your friend,
       Bob
       
       ==
       
       The following defaults are currently used in place of the expected
       fields from smtp:
       
       From: <configured login>
       To: <connection identity>
       Date: <datetime.now()>
       
    '''
    _title = "Email"
    _connection = None
    
    def configure(self, host="localhost", port=25, username="demo-user@domain.com", 
                  password="secret", use_tls=True, fail_silently=False):
        # the default information will not work, users need to configure this
        # in their settings
        
        # this is some commented out code that doesn't call django email packages
        self._username = username 
        self._host = host
        self._port = port
        self._password = password
        self._use_tls = use_tls 
        self._fail_silently = fail_silently
        self._connection = SMTPConnection(username=username,
                                          port=port,
                                          host=host,
                                          password=password,
                                          use_tls=use_tls,
                                          fail_silently=fail_silently)
    
    def send(self, message):
        destination = "%s" % (message.connection.identity)
        subject, from_email, to_email, text = self._get_email_params(message)
        email_message = EmailMessage(subject, text, from_email, to_email,
                                     connection=self._connection)
        
        # this is a fairly ugly hack to get html emails working properly
        if text.startswith("<html>"):
            email_message.content_subtype = "html"
        result = email_message.send(fail_silently=self._fail_silently)
        
    def start(self):
        backend.Backend.start(self)

    def stop(self):
        backend.Backend.stop(self)
        self.info("Shutting down...")

    def _get_email_params(self, message):
        """Get the parameters needed by the Django email client
           from a rapidsms message object. What is returned is a 
           4-element tuple containing: 
           (subject: a string
            from_email: a string
            to_email: a tuple
            text: the message body ) 
        """
        # todo: parsing of the subject/other params
        # check CRLFs and USE THEM! if there are only newlines.
        # this assumes that the message contains all or no CRLFs.
        # see: http://tools.ietf.org/html/rfc2822.html
        
        # another thing to note: this format doesn't like unicode
        text = str(message.text)
        if not "\r\n" in text:
            print "replacing LFs with CRLFs"
            text = text.replace("\n", "\r\n")
        else:
            print "Found CRLFs!"
        email_message = message_from_string(text)
        
        # amazingly these keys are actually not case sensitive
        if email_message.has_key("subject"):
            subject = email_message["subject"]
        else: 
            subject = ""
        
        # todo: Django email doesn't appear to honor this.
        # Maybe that's a good thing, as it prevents easy spoofing.
        if email_message.has_key("from"):
            from_string = email_message["from"]
        else: 
            from_string = self._username
        
        # always use the identity in the message for "to",
        # even if they specified one in the headers
        to_string = message.connection.identity
        if "," in to_string:
            to_ple = to_string.split(",") 
        else:
            to_ple = (to_string, )
            
        # todo: honor dates?  other params?  would all be 
        # made much easier by moving to standard python email
        # instead of django.  left as a future decision.
        return (subject, from_string, to_ple, email_message.get_payload())
     
    
        