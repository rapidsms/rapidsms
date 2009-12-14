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
        result_codes = {
            "0" : "no further user action required",
            "1" : "further user action required",
            "2" : "USSD terminated by network",
            "4" : "Operation not supported"
        }
        try:
            result_list = []
            result_string = ""
            result_lines = self.modem.run_ussd(code_string)
            for line in result_lines:
                if line.startswith("OK"):
                    continue
                else:
                    result_list.append(line)
            if len(result_list) > 0:
                # response string from network can be multiline, so
                # flatten these lines into a single string
                result_string = " ".join(result_list)
            else:
                raise("WTF")

            # this seems dodgy, but network should always reply with at 
            # least one line beginning with '+CUSD: #'
            if result_string[7].isdigit():
                result_code = result_string[7]
                if result_code != "2":
                    # TODO test on other networks. ORANGE SN consistently
                    # gives response code 2 when you run a valid USSD code,
                    # but other networks could give 0
                    return result_codes[result_code]
                else:
                    human_result = result_string.split('"')[1]
                    return human_result
            # not sure how it could get here but what the hell
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

        # disconnect from modem
        if self.modem is not None:
            self.modem.disconnect()
