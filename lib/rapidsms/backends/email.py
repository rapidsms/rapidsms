#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

"""
To use the emails backend, one needs to append 'email' to the list of 
available backends, like so:

    "email" :          {"ENGINE":  "rapidsms.backends.email", 
                        "smtp_host": "smtp.gmail.com",
                        "smtp_port": 587,
                        "imap_host": "imap.gmail.com",
                        "imap_port": 993,
                        "username": "rapidsms@domain.org",
                        "password": "rapidsms",
                        "use_tls":  "True"}

The following additional parameters are optional

fail_silently=False

Note that if fail_silently is False, then errors with message sending will
result in an exception being thrown.
"""

from __future__ import absolute_import
from .base import BackendBase
import imaplib
import time
import smtplib
import re


from datetime import datetime
from email import message_from_string
from email.mime.text import MIMEText

class Backend(BackendBase):
    '''Backend to interact with email.  Link this to an smtp and imap account.
       The account will be polled and every unread message will be sent (the 
       body) to the router as if it was an SMS.  As soon as messages are found
       they are marked read.  
       
       This backend creates EmailMessage messages, which are an extension of 
       messages that include a subject and mime_type.  Currently we do not
       do anything smart with attachments.
    '''
    _title = "Email"
    
    def configure(self, smtp_host="localhost", smtp_port=25,  
                  imap_host="localhost", imap_port=143,
                  username="demo-user@domain.com",
                  password="secret", 
                  use_tls=True, poll_interval=60):
        # the default information will not work, users need to configure this
        # in their settings
        self.debug("configuring email backend")
        
        self.smtp_host = smtp_host
        self.smtp_port = int(smtp_port)
        self.imap_host = imap_host
        self.imap_port = int(imap_port)
        self.username = username 
        self.password = password
        self.use_tls = use_tls 
        self.poll_interval = int(poll_interval)
        
    def send(self, email_message):
        # Create a text/plain message for now
        # TODO: support html formatted messages?
        msg = MIMEText(email_message.text)
        msg['Subject'] = getattr(email_message, "subject", None)
        msg['From'] = self.username 
        msg['To'] = email_message.peer
        s = smtplib.SMTP(host=self.smtp_host, port=self.smtp_port)
        s.ehlo()
        if self.use_tls:
            s.starttls()
        s.login(self.username, self.password)
        s.sendmail(self.username, [email_message.peer], msg.as_string())
        s.quit()
        
        
    def run(self):
        while self.running:
            # check for messages, if we find them, ship them off to the
            # router and go back to sleep
            messages = self._get_new_messages()
            if messages:
                for message in messages:
                    self.route(message)
                                    
            time.sleep(self.poll_interval)
            
    def _get_new_messages(self):
        self.debug("polling for new messages")
        imap_connection = imaplib.IMAP4_SSL(self.imap_host, self.imap_port)
        imap_connection.login(self.username, self.password)
        imap_connection.select()
        all_msgs = []
        # this assumes any unread message is a new message
        typ, data = imap_connection.search(None, 'UNSEEN')
        for num in data[0].split():
            typ, data = imap_connection.fetch(num, '(RFC822)')
            # get a rapidsms message from the data
            email_message = self.message_from_imap(data[0][1])
            all_msgs.append(email_message)
            # mark it read
            imap_connection.store(num, "+FLAGS", "\\Seen")
        imap_connection.close()
        imap_connection.logout()
        return all_msgs
    
    
    def message_from_imap(self, imap_mail):
        """From an IMAP message object, get a rapidsms message object"""
        parsed = message_from_string(imap_mail)
        from_user = parsed["From"] 
        # if the from format was something like:
        # "Bob User" <bob@users.com>
        # just pull out the relevant address part from within the carats.
        # Note that we don't currently do anything smart parsing email
        # addresses to make sure they are valid, we either just take
        # what we get, or take what we get between <>.    
        match = re.match(r"^.*<\s*(\S+)\s*>", from_user)
        if match:
            new_addr = match.groups()[0]
            self.debug("converting %s to %s" % (from_user, new_addr))
            from_user = new_addr
            
        subject = parsed["Subject"]
        date_string = parsed["Date"]
        # TODO: until we figure out how to generically parse dates, just use
        # the current time.  This appears to be the standard date format, but
        # currently timezone information is optional.
        # date = datetime.strptime(truncated_date, "%a, %d %b %Y %H:%M:%S")
        date = datetime.now()
        
        message_body = get_message_body(parsed)
        if not message_body:
            self.error("Got a poorly formed email.  Couldn't find any part with content-type text")
            # TODO: not sure how to handle this.  For now still route it with empty body
            message = self.message(from_user, "", date)
            message.subject = subject
            return message
            
        message = self.message(from_user, message_body.get_payload(), date)
        message.subject = subject
        message.mime_type = message_body.get_content_type()
        return message
    

def is_plaintext(email_message):
    """Whether a message is plaintext"""
    return re.match(r"^text/plain", email_message.get_content_type(), re.IGNORECASE)

def is_text(email_message):
    """Whether a message is text"""
    return re.match(r"^text/.*", email_message.get_content_type(), re.IGNORECASE)

def get_message_body(email_message):
    """Walk through the message parts, taking the first text/plain.
       if no text/plain (is this allowed?) will return the first
       text/html"""
    candidate = None
    if email_message.is_multipart():
        for message_part in email_message.walk():
            if is_plaintext(message_part):
                return message_part
            elif is_text(message_part) and candidate is not None:
                candidate = message_part
    else:
        # we don't really have a choice here
        return email_message
    return candidate
