#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8


import time
import pygsm
import Queue

from rapidsms.message import Message
from rapidsms.connection import Connection
from rapidsms.backends import Backend
import backend
from rapidsms import log
from rapidsms import utils

POLL_INTERVAL=2 # num secs to wait between checking for inbound texts
LOG_LEVEL_MAP = {
    'traffic':'info',
    'read':'info',
    'write':'info',
    'debug':'debug',
    'warn':'warning',
    'error':'error'
}

class Backend(Backend):
    _title = "pyGSM"
    
    def _log(self, modem, msg, level):
        # convert GsmModem levels to levels understood by
        # the rapidsms logger
        level = LOG_LEVEL_MAP[level]
        
        if self.modem_logger is not None:
            self.modem_logger.write(self,level,msg)
        else:
            self.router.log(level, msg)

    def configure(self, *args, **kwargs):
        self.modem = None
        self.modem_args = args
        
        # set max outbound text size
        if 'max_csm' in kwargs:
            self.max_csm = int(kwargs['max_csm'])
        else:
            self.max_csm = 1
        
        if self.max_csm>255:
            self.max_csm = 255
        if self.max_csm<1:
                self.max_csm = 1
                
        # make a modem log
        self.modem_logger = None
        if 'modem_log' in  kwargs:
            mlog = kwargs.pop('modem_log')
            level='info'
            if 'modem_log_level' in kwargs:
                level=kwargs.pop('modem_log_level')
            self.modem_logger = log.Logger(level=level, file=mlog, channel='pygsm')
            
        kwargs['logger'] = self._log
        self.modem_kwargs = kwargs
       
    def __chunker(self, message_text, max_csm=160):
        text = message_text 
        max_chars = max_csm
        print max_chars
        messages = []

        # if message text is longer than max_chars, see how
        # many messages we will need
        if len(text) > max_chars:
            full_msgs, remainder = divmod(len(text), max_chars)
            if remainder > 0:
                num_msgs = full_msgs + 1
            else:
                num_msgs = full_msgs

            # make list of all the words in text
            msg_words = text.split()

            # list of tuples (word, word_length)
            words_counts = [(w,len(w)) for w in msg_words]

            # construct messages
            for msg in range(num_msgs):
                chunk_construction = True
                chunk_chars = 0
                chunk_words = []
                while chunk_construction:
                    # make sure our chunk isnt too long and we 
                    # still have words to send
                    if chunk_chars < max_chars and len(words_counts) > 0:

                            # make sure we can fit this word's 
                            # characters and a space into this chunk
                            if ((chunk_chars + words_counts[0][1]) + 1 < max_chars):
                                word_count = words_counts.pop(0)
                                chunk_chars = chunk_chars + word_count[1] + 1
                                chunk_words.append(word_count[0])
                            else:
                                chunk = " ".join(chunk_words)
                                chunk_construction = False
                    else:
                        chunk = " ".join(chunk_words)
                        chunk_construction = False
                messages.append(chunk) 
                print chunk
            return messages
        else:
            return False


    def __send_sms(self, message):
        try:
            # TODO if message text is longer than self.max_csm,
            # send all of its chunks
            chunked = self.__chunker(message.text, 160)
            if chunked:
                for chunk in chunked:
                    self.modem.send_sms(
                        str(message.connection.identity),
                        chunk)#,
                        #max_messages=self.max_csm)
                    # Mattel seems to get overwhelmed
                    # TODO use More Messages to Send AT+CMMS
                    # when sending several messages
                    time.sleep(1)
            else:
                self.modem.send_sms(
                    str(message.connection.identity),
                    message.text)#,max_messages=70)
        except ValueError, err:
            # TODO: Pass this error info on to caller!
            self.error('Error sending message: %s' % err)

    def __run_ussd(self, code_string):
        try:
            result = self.modem.run_ussd(code_string)
            return result

        except ValueError, err:
            self.error('Error running USSD code: %s' % err)
        
    def run(self):
        while self._running:
            # check for new messages
            msg = self.modem.next_message()
        
            if msg is not None:
                # we got an sms! create RapidSMS Connection and
                # Message objects, and hand it off to the router
                c = Connection(self, msg.sender)
                m = Message(
                            connection=c, 
                            text=msg.text,
                            date=utils.to_naive_utc_dt(msg.sent)
                            )
                self.router.send(m)
                
            # process all outbound messages
            while True:
                try:
                    self.__send_sms(self._queue.get_nowait())
                except Queue.Empty:
                    # break out of while
                    break
                
            # poll for new messages
            # every POLL_INTERVAL seconds
            time.sleep(POLL_INTERVAL)
    
    def start(self):
        self.modem = pygsm.GsmModem(
            *self.modem_args,
            **self.modem_kwargs)

        # If we got the connection, call superclass to
        # start the run loop--it just sets self._running to True
        # and calls run.
        if self.modem is not None:
            backend.Backend.start(self)

    def stop(self):
        # call superclass to stop--sets self._running
        # to False so that the 'run' loop will exit cleanly.
        backend.Backend.stop(self)
=======

from ..models import Connection
from ..messages.incoming import IncomingMessage
from .base import BackendBase


class Backend(BackendBase):
    _title = "pyGSM"

    # number of seconds to wait between
    # polling the modem for incoming SMS
    POLL_INTERVAL = 10

    # time to wait for the start method to
    # complete before assuming that it failed
    MAX_CONNECT_TIME = 10


    def configure(self, **kwargs):

        # strip any config settings that
        # obviously aren't for the modem
        for arg in ["title", "name"]:
            if arg in kwargs:
                kwargs.pop(arg)

        # store the rest to pass on to the
        # GsmModem() when RapidSMS starts
        self.modem_kwargs = kwargs
        self.modem = None


    def __str__(self):
        return self._title


    def _wait_for_modem(self):
        """
        Blocks until this backend has connected to and initialized the modem,
        waiting for a maximum of self.MAX_CONNECT_TIME (default=10) seconds.
        Returns true when modem is ready, or false if it times out.
        """

        # if the modem isn't present yet, this message is probably being sent by
        # an application during startup from the main thread, before this thread
        # has connected to the modem. block for a short while before giving up.
        for n in range(0, self.MAX_CONNECT_TIME*10):
            if self.modem is not None: return True
            time.sleep(0.1)

        # timed out. we're still not connected
        # this is bad news, but not fatal, so warn
        self.warning("Timed out while waiting for modem")
        return False


    def send(self, message):

        # if this message is being sent from the start method of
        # an app (which is run in the main thread), this backend
        # may not have had time to start up yet. wait for it
        if not self._wait_for_modem():
            return False

        # attempt to send the message
        # failure is bad, but not fatal
        was_sent = self.modem.send_sms(
            str(message.connection.identity),
            message.text)

        if was_sent: self.sent_messages += 1
        else:        self.failed_messages += 1

        return was_sent


    def gsm_log(self, modem, str, level):
        self.debug("%s: %s" % (level, str))


    def status(self):

        # abort if the modem isn't connected
        # yet. there's no status to fetch
        if not self._wait_for_modem():
            return None

        csq = self.modem.signal_strength()

        # convert the "real" signal
        # strength into a 0-4 scale
        if   not csq:   level = 0
        elif csq >= 30: level = 4
        elif csq >= 20: level = 3
        elif csq >= 10: level = 2
        else:           level = 1

        vars = {
            "_signal":  level,
            "_title":   self.title,
            "Messages Sent": self.sent_messages,
            "Messages Received": self.received_messages }

        # pygsm can return the name of the network
        # operator since b19cf3. add it if we can
        if hasattr(self.modem, "network"):
            vars["Network Operator"] = self.modem.network

        return vars


    def run(self):
        while self.running:
            self.info("Polling modem for messages")
            msg = self.modem.next_message()

            if msg is not None:
                self.received_messages += 1

                # we got an sms! hand it off to the
                # router to be dispatched to the apps
                x = self.message(msg.sender, msg.text)
                self.router.incoming_message(x)

            # wait for POLL_INTERVAL seconds before continuing
            # (in a slightly bizarre way, to ensure that we abort
            # as soon as possible when the backend is asked to stop)
            for n in range(0, self.POLL_INTERVAL*10):
                if not self.running: return None
                time.sleep(0.1)


    def start(self):
        self.sent_messages = 0
        self.failed_messages = 0
        self.received_messages = 0

        # connect to the modem and boot it to start receiving incoming
        # messages. if connection fails, the router will retry shortly
        self.modem = pygsm.GsmModem(
            logger=self.gsm_log,
            **self.modem_kwargs
        ).boot()

        # call the superclass to start the run loop -- it just sets
        # ._running to True and calls run, but let's not duplicate it.
        BackendBase.start(self)


    def stop(self):

        # call superclass to stop--sets self._running
        # to False so that the 'run' loop will exit cleanly.
        BackendBase.stop(self)

        # disconnect from modem
        if self.modem is not None:
            self.modem.disconnect()
