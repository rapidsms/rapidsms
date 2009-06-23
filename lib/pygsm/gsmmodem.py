#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4 encoding=utf8


from __future__ import with_statement


# arch: pacman -S python-pyserial
# debian/ubuntu: apt-get install python-serial
import serial

# debian/ubuntu: apt-get install python-tz
import pytz 

import re, datetime, time
import errors, message
import traceback
import threading
import codecs
import gsmcodecs

# Constants
CMGL_STATUS="REC UNREAD" 
CMGL_MATCHER=re.compile(r'^\+CMGL: (\d+),"(.+?)","(.+?)",*?,"(.+?)".*?$')
HEX_MATCHER=re.compile(r'^[0-9a-f]+$')

class GsmModem(object):
    """pyGSM is a Python module which uses pySerial to provide a nifty
       interface to send and receive SMS via a GSM Modem. It was ported
       from RubyGSM, and provides (almost) all of the same features. It's
       easy to get started:

          # create a GsmModem object:
          >>> import pygsm
          >>> modem = pygsm.GsmModem(port="/dev/ttyUSB0")

          # harass Evan over SMS:
          # (try to do this before 11AM)
          >>> modem.send_sms("+13364130840", "Hey, wake up!")

          # check for incoming SMS:
          >>> print modem.next_message()
          <pygsm.IncomingMessage from +13364130840: "Leave me alone!">


       There are various ways of polling for incoming messages -- a choice
       which has been deliberately left to the application author (unlike
       RubyGSM). Execute `python -m pygsm.gsmmodem` to run this example:

          # connect to the modem
          modem = pygsm.GsmModem(port=sys.argv[1])

          # check for new messages every two
          # seconds for the rest of forever
          while True:
              msg = modem.next_message()

              # we got a message! respond with
              # something useless, as an example
              if msg is not None:
                  msg.respond("Thanks for those %d characters!" %
                      len(msg.text))

              # no messages? wait a couple
              # of seconds and try again
              else: time.sleep(2)


       pyGSM is distributed via GitHub:
       http://github.com/adammck/pygsm

       Bugs reports (especially for
       unsupported devices) are welcome:
       http://github.com/adammck/pygsm/issues"""


    # override these after init, and
    # before boot. they're not sanity
    # checked, so go crazy.
    cmd_delay = 0.1
    retry_delay = 2
    max_retries = 10
    modem_lock = threading.RLock()
    
    
    def __init__(self, *args, **kwargs):
        """Creates, connects to, and boots a GSM Modem. All of the arguments
           are optional (although "port=" should almost always be provided),
           and passed along to serial.Serial.__init__ verbatim. For all of
           the possible configration options, see:

           http://pyserial.wiki.sourceforge.net/pySerial#tocpySerial10

           Alternatively, a single "device" kwarg can be passed, which overrides
           the default proxy-args-to-pySerial behavior. This is useful when testing,
           or wrapping the serial connection with some custom logic."""

        if "logger" in kwargs:
            self.logger = kwargs.pop("logger")
        
        # if a ready-made device was provided, store it -- self.connect
        # will see that we're already connected, and do nothing. we'll
        # just assume it quacks like a serial port
        if "device" in kwargs:
            self.device = kwargs.pop("device")

            # if a device is given, the other args are never
            # used, so were probably included by mistake.
            if len(args) or len(kwargs):
                raise(TypeError("__init__() does not accept other arguments when a 'device' is given"))

        # for regular serial connections, store the connection args, since
        # we might need to recreate the serial connection again later
        else:
            self.device_args = args
            self.device_kwargs = kwargs

        # to cache parts of multi-part messages
        # until the last part is delivered
        self.multipart = {}

        # to store unhandled incoming messages
        self.incoming_queue = []

        # boot the device on init, to fail as
        # early as possible if it can't be opened
        self.boot()
    
    
    LOG_LEVELS = {
        "traffic": 4,
        "read":    4,
        "write":   4,
        "debug":   3,
        "warn":    2,
        "error":   1 }
    
    
    def _log(self, str, type="debug"):
        """Proxies a log message to this Modem's logger, if one has been set.
           This is useful for applications embedding pyGSM that wish to show
           or log what's going on inside.

           The *logger* should be a function with three arguments:
             modem:   a reference to this GsmModem instance
             message: the log message (a unicode string)
             type:    a string contaning one of the keys
                      of GsmModem.LOG_LEVELS, indicating
                      the importance of this message.

           GsmModem.__init__ accepts an optional "logger" kwarg, and a minimal
           (dump to STDOUT) logger is available at GsmModem.logger:

           >>> GsmModem("/dev/ttyUSB0", logger=GsmModem.logger)"""
        
        if hasattr(self, "logger"):
            self.logger(self, str, type)
    
    
    @staticmethod
    def logger(modem, message, type):
        print "%8s %s" % (type, message)
    
    
    def connect(self, reconnect=False):
        """Creates the connection to the modem via pySerial, optionally
           killing and re-creating any existing connection."""
           
        self._log("Connecting")
        
        # if no connection exists, create it
        # the reconnect flag is irrelevant
        if not hasattr(self, "device") or (self.device is None):
            with self.modem_lock:
                self.device = serial.Serial(
                    *self.device_args,
                    **self.device_kwargs)
                
        # the port already exists, but if we're
        # reconnecting, then kill it and recurse
        # to recreate it. this is useful when the
        # connection has died, but nobody noticed
        elif reconnect:
            
            self.disconnect()
            self.connect(False)

        return self.device


    def disconnect(self):
        """Disconnects from the modem."""
        
        self._log("Disconnecting")
        
        # attempt to close and destroy the device
        if hasattr(self, "device") and (self.device is None):
            with self.modem_lock:
                if self.device.isOpen():
                    self.device.close()
                    self.device = None
                    return True
        
        # for some reason, the device
        # couldn't be closed. it probably
        # just isn't open yet
        return False


    def set_modem_config(self):
        """initialize the modem configuration with settings needed to process
           commands and send/receive SMS.
        """
        
        # set some sensible defaults, to make
        # the various modems more consistant
        self.command("ATE0",      raise_errors=False) # echo off
        self.command("AT+CMEE=1", raise_errors=False) # useful error messages
        self.command("AT+WIND=0", raise_errors=False) # disable notifications
        # switch to text mode, and make sure it's a mode that handles
        # latin characters
        self.command('AT+CSCS="HEX"'                ) # Default encoding for serial line comm
        self.command("AT+CMGF=1"                    ) # switch to TEXT mode

        # enable new message notification
        self.command(
            "AT+CNMI=2,2,0,0,0",
            raise_errors=False)


    def boot(self, reboot=False):
        """Initializes the modem. Must be called after init and connect,
           but before doing anything that expects the modem to be ready."""
        
        self._log("Booting")
        
        if reboot:
            # If reboot==True, force a reconnection and full modem reset. SLOW
            self.connect(reconnect=True)
            self.command("AT+CFUN=1")
        else:
            # else just verify connection
            self.connect()

        # In both cases, reset the modem's config
        self.set_modem_config()        

        # And check for any waiting messages PRIOR to setting
        # the CNMI call--this is not supported by all modems--
        # in which case we catch the exception and plow onward
        try:
            self._fetch_stored_messages()
        except errors.GsmError:
            pass


    def reboot(self):
        """Forces a reconnect to the serial port and then a full modem reset to factory
           and reconnect to GSM network. SLOW.
        """
        self.boot(reboot=True)


    def _write(self, str):
        """Write a string to the modem."""
        
        self._log(repr(str), "write")

        try:
            self.device.write(str)

        # if the device couldn't be written to,
        # wrap the error in something that can
        # sensibly be caught at a higher level
        except OSError, err:
            raise(errors.GsmWriteError)


    def _read(self, read_term=None, read_timeout=None):
        """Read from the modem (blocking) until _terminator_ is hit,
           (defaults to \r\n, which reads a single "line"), and return."""
        
        buffer = []

        # if a different timeout was requested just
        # for _this_ read, store and override the
        # current device setting (not thread safe!)
        if read_timeout is not None:
            old_timeout = self.device.timeout
            self.device.timeout = read_timeout

        def __reset_timeout():
            """restore the device's previous timeout
               setting, if we overrode it earlier."""
            if read_timeout is not None:
                self.device.timeout =\
                    old_timeout

        # the default terminator reads
        # until a newline is hit
        if not read_term:
            read_term = "\r\n"

        while(True):
            buf = self.device.read()
            buffer.append(buf)

            # if a timeout was hit, raise an exception including the raw data that
            # we've already read (in case the calling func was _expecting_ a timeout
            # (wouldn't it be nice if serial.Serial.read returned None for this?)
            if buf == "":
                __reset_timeout()
                raise(errors.GsmReadTimeoutError(buffer))

            # if last n characters of the buffer match the read
            # terminator, return what we've received so far
            if buffer[-len(read_term)::] == list(read_term):
                buf_str = "".join(buffer)
                __reset_timeout()

                self._log(repr(buf_str), "read")
                return buf_str


    def _wait(self, read_term=None, read_timeout=None):
        """Read from the modem (blocking) one line at a time until a response
           terminator ("OK", "ERROR", or "CMx ERROR...") is hit, then return
           a list containing the lines."""
        buffer = []

        # keep on looping until a command terminator
        # is encountered. these are NOT the same as the
        # "read_term" argument - only OK or ERROR is valid
        while(True):
            buf = self._read(
                read_term=read_term,
                read_timeout=read_timeout)

            buf = buf.strip()
            buffer.append(buf)

            # most commands return OK for success, but there
            # are some exceptions. we're not checking those
            # here (unlike RubyGSM), because they should be
            # handled when they're _expected_
            if buf == "OK":
                return buffer

            # some errors contain useful error codes, so raise a
            # proper error with a description from pygsm/errors.py
            m = re.match(r"^\+(CM[ES]) ERROR: (\d+)$", buf)
            if m is not None:
                type, code = m.groups()
                raise(errors.GsmModemError(type, int(code)))

            # ...some errors are not so useful
            # (at+cmee=1 should enable error codes)
            if buf == "ERROR":
                raise(errors.GsmModemError)


    SCTS_FMT = "%y/%m/%d,%H:%M:%S"
    

    def _parse_incoming_timestamp(self, timestamp):
        """Parse a Service Center Time Stamp (SCTS) string into a Python datetime
           object, or None if the timestamp couldn't be parsed. The SCTS format does
           not seem to be standardized, but looks something like: YY/MM/DD,HH:MM:SS."""

        # timestamps usually have trailing timezones, measured
        # in 15-minute intervals (?!), which is not handled by
        # python's datetime lib. if _this_ timezone does, chop
        # it off, and note the actual offset in minutes
        tz_pattern = r"[-+](\d+)$"
        m = re.search(tz_pattern, timestamp)
        if m is not None:
            timestamp = re.sub(tz_pattern, "", timestamp)
            tz_offset = datetime.timedelta(minutes=int(m.group(0)) * 15)

        # we won't be modifying the output, but
        # still need an empty timedelta to subtract
        else: tz_offset = datetime.timedelta()

        # attempt to parse the (maybe modified) timestamp into
        # a time_struct, and convert it into a datetime object
        try:
            time_struct = time.strptime(timestamp, self.SCTS_FMT)
            dt = datetime.datetime(*time_struct[:6], tzinfo=pytz.utc)

            # patch the time to represent LOCAL TIME, since
            # the datetime object doesn't seem to represent
            # timezones... at all
            return dt - tz_offset

        # if the timestamp couldn't be parsed, we've encountered
        # a format the pyGSM doesn't support. this sucks, but isn't
        # important enough to explode like RubyGSM does
        except ValueError:
            traceback.print_exc()
            return None


    def _parse_incoming_sms(self, lines):
        """Parse a list of lines (the output of GsmModem._wait), to extract any
           incoming SMS and append them to GsmModem.incoming_queue. Returns the
           same lines with the incoming SMS removed. Other unsolicited data may
           remain, which must be cropped separately."""

        output_lines = []
        n = 0

        # iterate the lines like it's 1984
        # (because we're patching the array,
        # which is hard work for iterators)
        while n < len(lines):

            # not a CMT string? add it back into the
            # output (since we're not interested in it)
            # and move on to the next
            if lines[n][0:5] != "+CMT:":
                output_lines.append(lines[n])
                n += 1
                continue

            # since this line IS a CMT string (an incoming
            # SMS), parse it and store it to deal with later
            m = re.match(r'^\+CMT: "(.+?)",.*?,"(.+?)".*?$', lines[n])
            if m is None:

                # couldn't parse the string, so just move
                # on to the next line. TODO: log this error
                n += 1
                next

            # extract the meta-info from the CMT line,
            # and the message from the FOLLOWING line
            sender, timestamp = m.groups()
            text = lines[n+1].strip()

            # notify the network that we accepted
            # the incoming message (for read receipt)
            # BEFORE pushing it to the incoming queue
            # (to avoid really ugly race condition if
            # the message is grabbed from the queue
            # and responded to quickly, before we get
            # a chance to issue at+cnma)
            try:
                self.command("AT+CNMA")

            # Some networks don't handle notification, in which case this
            # fails. Not a big deal, so ignore.
            except errors.GsmError:
                #self.log("Receipt acknowledgement (CNMA) was rejected")
                # TODO: also log this!
                pass

            # (i'm using while/break as an alternative to catch/throw
            # here, since python doesn't have one. we might abort early
            # if this is part of a multi-part message, but not the last
            while True:

                # multi-part messages begin with ASCII 130 followed
                # by "@" (ASCII 64). TODO: more docs on this, i wrote
                # this via reverse engineering and lost my notes
                if (ord(text[0]) == 130) and (text[1] == "@"):
                    part_text = text[7:]

                    # ensure we have a place for the incoming
                    # message part to live as they are delivered
                    if sender not in self.multipart:
                        self.multipart[sender] = []

                    # append THIS PART
                    self.multipart[sender].append(part_text)

                    # abort if this is not the last part
                    if ord(text[5]) != 173:
                        break

                    # last part, so switch out the received
                    # part with the whole message, to be processed
                    # below (the sender and timestamp are the same
                    # for all parts, so no change needed there)
                    text = "".join(self.multipart[sender])
                    del self.multipart[sender]

                # store the incoming data to be picked up
                # from the attr_accessor as a tuple (this
                # is kind of ghetto, and WILL change later)
                self._add_incoming(timestamp, sender, text)

                # don't loop! the only reason that this
                # "while" exists is to jump out early
                break

            # jump over the CMT line, and the
            # text line, and continue iterating
            n += 2

        # return the lines that we weren't
        # interested in (almost all of them!)
        return output_lines


    def _add_incoming(self, timestamp, sender, text):
        if text is None or len(text)==0:
            self._log("Blank inbound text, ignore")
        # try to decode inbound message
        text=text.decode('hex')
        try:
            text=decode('gsm')
        except:
            # is it UCS2?
            if len(text)>0 and (len(text) % 4)==0:
                bom=text[0:4]
                if bom==codecs.BOM_UTF16_LE.encode('hex') or \
                        bom==codecs.BOM_UTF16_BE.encode('hex'):
                    text=text.decode('utf_16')
                else:
                    text=text.decode('utf_16_be')

        # create and store the IncomingMessage object
        time_sent = self._parse_incoming_timestamp(timestamp)
        msg = message.IncomingMessage(self, sender, time_sent, text)
        self.incoming_queue.append(msg)
        return msg


    def command(self, cmd, read_term=None, read_timeout=None, write_term="\r", raise_errors=True):
        """Issue a single AT command to the modem, and return the sanitized
           response. Sanitization removes status notifications, command echo,
           and incoming messages, (hopefully) leaving only the actual response
           from the command.
           
           If Error 515 (init or command in progress) is returned, the command
           is automatically retried up to _GsmModem.max_retries_ times."""

        # keep looping until the command
        # succeeds or we hit the limit
        retries = 0
        while retries < self.max_retries:
            try:

                # issue the command, and wait for the
                # response
                with self.modem_lock:
                    self._write(cmd + write_term)
                    lines = self._wait(
                        read_term=read_term,
                        read_timeout=read_timeout)

                # no exception was raised, so break
                # out of the enclosing WHILE loop
                break

            # Outer handler: if the command caused an error,
            # maybe wrap it and return None
            except errors.GsmError, err:
                # if GSM Error 515 (init or command in progress) was raised,
                # lock the thread for a short while, and retry. don't lock
                # the modem while we're waiting, because most commands WILL
                # work during the init period - just not _cmd_
                if getattr(err, "code", None) == 515:
                    time.sleep(self.retry_delay)
                    retries += 1
                    continue

                # if raise_errors is disabled, it doesn't matter
                # *what* went wrong - we'll just ignore it
                if not raise_errors:
                    return None

                # otherwise, allow errors to propagate upwards,
                # and hope someone is waiting to catch them
                else: 
                    raise(err)

        # if the first line of the response echoes the cmd
        # (it shouldn't, if ATE0 worked), silently drop it
        if lines[0] == cmd:
            lines.pop(0)

        # remove all blank lines and unsolicited
        # status messages. i can't seem to figure
        # out how to reliably disable them, and
        # AT+WIND=0 doesn't work on this modem
        lines = [
            line
            for line in lines
            if line      != "" or\
               line[0:6] == "+WIND:" or\
               line[0:6] == "+CREG:" or\
               line[0:7] == "+CGRED:"]

        # parse out any incoming sms that were bundled
        # with this data (to be fetched later by an app)
        lines = self._parse_incoming_sms(lines)

        # rest up for a bit (modems are
        # slow, and get confused easily)
        time.sleep(self.cmd_delay)

        return lines


    def query(self, cmd, prefix=None):
        """Issues a single AT command to the modem, and returns the relevant
           part of the response. This only works for commands that return a
           single line followed by "OK", but conveniently, this covers almost
           all AT commands that I've ever needed to use.

           For all other commands, returns None."""

        # issue the command, which might return incoming
        # messages, but we'll leave them in the queue
        out = self.command(cmd)

        # the only valid response to a "query" is a
        # single line followed by "OK". if all looks
        # well, return just the single line
        if(len(out) == 2) and (out[-1] == "OK"):
            if prefix is None:
                return out[0].strip()

            # if a prefix was provided, check that the
            # response starts with it, and return the
            # cropped remainder
            else:
                if out[0][:len(prefix)] == prefix:
                    return out[0][len(prefix):].strip()

        # something went wrong, so return the very
        # ambiguous None. it's better than blowing up
        return None


    def send_sms(self, recipient, text):
        """Sends an SMS to _recipient_ containing _text_. Some networks
           will automatically chunk long messages into multiple parts,
           and reassembled them upon delivery, but some will silently
           drop them. At the moment, pyGSM does nothing to avoid this,
           so try to keep _text_ under 160 characters."""

        old_mode = None
        with self.modem_lock:
            # outer try to catch any error and make sure to
            # get the modem out of 'waiting for data' mode
            try:
                # try to catch write timeouts
                try:
                    gsm_mode=True
                    # try for attempting to down-code to gsm char table
                    try:
                        text = text.encode('gsm').encode('hex')
                    except UnicodeEncodeError as uerr:
                        gsm_mode=False
                        # uh-oh, not in standard 'latin' characters
                        # this message will require UTF16 (big endian)
                        # TODO: Check for length!! (must be 70 char or less)
                        text = text.encode('utf_16_be').encode('hex')
                    
                    if gsm_mode:
                        cs='GSM'
                    else:
                        # hex mode
                        enc='8'
                    
                    csmp_code="17,167,0,"+enc
                    self.command("AT+CSMP=%s" % csmp_code)
                    result = self.command(
                        'AT+CMGS="%s"' % (recipient),
                        read_timeout=1)

                # if no error is raised within the timeout period,
                # and the text-mode prompt WAS received, send the
                # sms text, wait until it is accepted or rejected
                # (text-mode messages are terminated with ascii char 26
                # "SUBSTITUTE" (ctrl+z)), and return True (message sent)
                except errors.GsmReadTimeoutError, err:
                    if err.pending_data[0] == ">":
                        self.command(text, write_term=chr(26))
                        return True

                    # a timeout was raised, but no prompt nor
                    # error was received. i have no idea what
                    # is going on, so allow the error to propagate
                    else:
                        raise

                finally:
                    pass
                        
            # for all other errors...
            # (likely CMS or CME from device)
            except Exception as err:
                traceback.print_exc()
                # whatever went wrong, break out of the
                # message prompt. if this is missed, all
                # subsequent writes will go into the message!
                self._write(chr(27))

                # rule of thumb: pyGSM is meant to be embedded,
                # so DO NOT EVER allow exceptions to propagate
                # (obviously, this sucks. there should be an
                # option, at least, but i'm being cautious)
                return None


    def hardware(self):
        """Returns a dict of containing information about the physical
           modem. The contents of each value are entirely manufacturer
           dependant, and vary wildly between devices."""

        return {
            "manufacturer": self.query("AT+CGMI"),
            "model":        self.query("AT+CGMM"),
            "revision":     self.query("AT+CGMR"),
            "serial":       self.query("AT+CGSN") }


    def signal_strength(self):
        """Returns an integer between 1 and 99, representing the current
           signal strength of the GSM network, False if we don't know, or
           None if the modem can't report it."""

        data = self.query("AT+CSQ")
        md = re.match(r"^\+CSQ: (\d+),", data)

        # 99 represents "not known or not detectable". we'll
        # return False for that (so we can test it for boolean
        # equality), or an integer of the signal strength.
        if md is not None:
            csq = int(md.group(1))
            return csq if csq < 99 else False

        # the response from AT+CSQ couldn't be parsed. return
        # None, so we can test it in the same way as False, but
        # check the type without raising an exception
        return None


    def wait_for_network(self):
        """Blocks until the signal strength indicates that the
           device is active on the GSM network. It's a good idea
           to call this before trying to send or receive anything."""

        while True:
            csq = self.signal_strength()
            if csq: return csq
            time.sleep(1)


    def ping(self):
        """Sends the "AT" command to the device, and returns true
           if it is acknowledged. Since incoming notifications and
           messages are intercepted automatically, this is a good
           way to poll for new messages without using a worker
           thread like RubyGSM."""

        try:
            self.command("AT")
            return True

        except errors.GsmError:
            return None


    def _strip_ok(self,lines):
        """Strip 'OK' from end of command response"""
        if lines is not None and len(lines)>0 and \
                lines[-1]=='OK':
            lines=lines[:-1] # strip last entry
        return lines


    def _fetch_stored_messages(self):
        """Fetch stored messages with CMGL and add to incoming queue
           Return number fetched"""

        lines = self._strip_ok(self.command('AT+CMGL="%s"' % CMGL_STATUS))
        # loop through all the lines attempting to match CMGL lines (the header)
        # and then match NOT CMGL lines (the content)
        # need to seed the loop first 'cause Python no like 'until' loops
        num_found=0
        if len(lines)>0:
            m=CMGL_MATCHER.match(lines[0])

        while len(lines)>0:
            if m is None:
                # couldn't match OR no text data following match
                raise(errors.GsmReadError())

            # if here, we have a match AND text
            # start by popping the header (which we have stored in the 'm'
            # matcher object already)
            lines.pop(0)

            # now put the captures into independent vars
            index, status, sender, timestamp = m.groups()

            # now loop through, popping content until we get
            # the next CMGL or out of lines
            msg_text=list()
            while len(lines)>0:
                m=CMGL_MATCHER.match(lines[0])
                if m is not None:
                    # got another header, get out
                    break
                else:
                    msg_text.append(lines.pop(0))

            # get msg text
            msg_text=''.join(msg_text)

            # now create message
            self._add_incoming(timestamp,sender,msg_text)
            num_found+=1

        return num_found


    def next_message(self, ping=True, fetch=True):
        """Returns the next waiting IncomingMessage object, or None if the
           queue is empty. The optional _ping_ and _fetch_ parameters control
           whether the modem is pinged (to allow new messages to be delivered
           instantly, on those modems which support it) and queried for unread
           messages in storage, which can both be disabled in case you're
           already polling in a separate thread."""

        # optionally ping the modem, to give it a
        # chance to deliver any waiting messages
        if ping:
            self.ping()

        # optionally check the storage for unread messages.
        # we must do this just as often as ping, because most
        # handsets don't support CNMI-style delivery
        if fetch:
            self._fetch_stored_messages()

        # abort if there are no messages waiting
        if not self.incoming_queue:
            return None

        # remove the message that has been waiting
        # longest from the queue, and return it
        return self.incoming_queue.pop(0)




if __name__ == "__main__":

    import sys, re
    if len(sys.argv) >= 2:

        # the first argument is SERIAL PORT
        # (required, since we have no autodetect yet)
        port = sys.argv[1]

        # all subsequent options are parsed as key=value
        # pairs, to be passed on to GsmModem.__init__ as
        # kwargs, to configure the serial connection
        conf = dict([
            arg.split("=", 1)
            for arg in sys.argv[2:]
            if arg.find("=") > -1
        ])

        # dump the connection settings
        print "pyGSM Demo App"
        print "  Port: %s" % (port)
        print "  Config: %r" % (conf)
        print

        # connect to the modem (this might hang
        # if the connection settings are wrong)
        print "Connecting to GSM Modem..."
        modem = GsmModem(port=port, **conf)
        print "Waiting for incoming messages..."

        # check for new messages every two
        # seconds for the rest of forever
        while True:
            msg = modem.next_message()

            # we got a message! respond with
            # something useless, as an example
            if msg is not None:
                print "Got Message: %r" % msg
                msg.respond("Received: %d characters '%s'" %
                    (len(msg.text),msg.text))

            # no messages? wait a couple
            # of seconds and try again
            else: time.sleep(2)

    # the serial port must be provided
    # we're not auto-detecting, yet
    else:
        print "Usage: python -m pygsm.gsmmodem PORT [OPTIONS]"
