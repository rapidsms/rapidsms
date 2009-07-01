#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8


from __future__ import with_statement

import re, datetime
import math
import pytz
import codecs
import gsmcodecs

max_gsm_text_len = 160
max_csm_gsm_text_len = 152
max_ucs2_text_len = 70
max_csm_ucs2_text_len = 67
max_csm_segments = 255

class SmsParseException(Exception):
    pass

class SmsEncodeExcpetion(Exception):
    pass

class GsmPdu(object):
    pass

class OutboundPdu(GsmPdu):
    """
    Formatted outbound PDU. Basically just
    a struct.
  
    Don't instantiate directly! Use 'get_outbound_pdus()'
    which will return a list of PDUs needed to
    send the message

    """
    
    def __init__(self, text, sender, csm_ref=None, csm_seq=None, csm_total=None):
        self.sender_number = sender
        self.text = text
        self.is_csm = csm_ref is not None
        self.csm_ref = csm_ref
        self.csm_seq = csm_seq
        self.csm_total = csm_total
        
        try:
            self.encoded_text = self.text.encode('gsm')
            self.encoding = 'gsm'
        except:
            self.encoded_text = self.text.encode('utf_16_be')
            self.encoding='ucs2'

        @property
        def pdu_str(self):
            if self.is_csm:
                max = (max_csm_gsm_text_len if self.encoding=='gsm'
                       else max_csm_ucs2_text_len)
            else:
                max = (max_gsm_text_len if self.encoding=='gsm'
                       else max_ucs2_text_len)
            
            if len(text)>max:
                raise SmsEncodeError('Text length too great')

            # now put the PDU string together
            # first octet is SMSC info, 00 means get from stored on SIM
            pdu=['00'] 
            # Next is 'SMS-SUBMIT First Octet' -- '11' means submit w/validity. 
            # '51' means Concatendated SM w/validity
            pdu.append('51' if self.is_cms else '11') 
            # Next is 'message' reference. '00' means phone can set this
            pdu.append('00')
            # now sender number, first type
            if self.sender_number[0]=='+':
                num = self.sender_number[1:]
                type = '91' # international
            else:
                num = self.sender_number
                type = 'a8' # national number
            
            # length
            num_len = len(num)
            # twiddle it
            num = _twiddle(num, False)
            pdu.append(str(num)) # length
            pdu.append(type)
            pdu.append(num)
            
            # now protocol ID
            pdu.append('00')
            
            # data coding scheme
            pdu.append('00' if self.encoding=='gsm' else '08')

            # validity period, just default to 4 days
            pdu.append('aa')

            # Now the fun part! User data length and User data
            # If we are a CSM, user data length is encoded text+header
            # otherwise it's just the text length. So first let's
            # encode
            
                
class ReceivedGsmPdu(GsmPdu):
    """
    A nice little class to parse a PDU and give you useful
    properties.

    Maybe one day it will let you set text and sender info and 
    ask it to write itself out as a PDU!

    """
    def __init__(self, pdu_str):
        # hear are the properties that are set below in the 
        # ugly parse code. 

        self.tp_mms=False # more messages to send
        self.tp_sri=False # status report indication
        self.sender_number=None # phone number of sender as string
        self.sent_ts=None # Datetime of when SMSC stamped the message, roughly when sent
        self.text=None # string of message contents
        self.pdu=pdu_str # original data as a string
        self.is_csm=False # is this one of a sequence of concatenated messages?
        self.csm_ref=0 # reference number
        self.csm_seq=0 # this chunks sequence num, 1-based
        self.csm_total=0 # number of chunks total
        self.encoding=None # either 'gsm' or 'ucs2'

        self.__parse_pdu()
    
    def dump(self):
        """
        Return a useful multiline rep of self

        """
        header='From: %s\nLength: %s' % (self.sender_number, len(self.text))
        csm_info=''
        if self.is_csm:
            csm_info='\nCSM: %d of %d for Ref# %d' % (self.csm_seq, self.csm_total,self.csm_ref)
        return '%s%s\nMessage: \n%s\n' % (header,csm_info,self.text)

    """
    This is truly hideous, just don't look below this line!
    
    It's times like this that I miss closed-compiled source...

    """

    def __parse_pdu(self):
        # grab smsc header, and throw away
        # length is held in first octet
        smsc_len,pdu=_consume_bytes(self.pdu,1)

        # consume smsc header
        c,pdu=_consume(pdu, smsc_len)

        # grab the deliver octect
        deliver_attrs,pdu=_consume_bytes(pdu,1)

        if deliver_attrs & 0x03 != 0:
            raise SmsParseException("Not a SMS-DELIVER, we ignore")

        self.tp_mms=deliver_attrs & 0x04 # more messages to send
        self.tp_sri=deliver_attrs & 0x20 # Status report indication
        tp_udhi=deliver_attrs & 0x40 # There is a user data header in the user data portion

        # get the sender number. 
        # First the length which is given in 'nibbles' (half octets)
        # so divide by 2 and round up for odd
        sender_dec_len,pdu=_consume_bytes(pdu,1)
        sender_len=int(math.ceil(sender_dec_len/2.0))
        
        # next is sender id type
        sender_type,pdu=_consume(pdu,1)

        # now the number itself, (unparsed)
        num,pdu=_consume(pdu,sender_len)

        # now parse the number
        self.sender_number=_parse_phone_num(sender_type,num)

        # now the protocol id
        # we only understand SMS (0)
        tp_pid,pdu=_consume_bytes(pdu,1)
        if tp_pid != 0:
            # can't deal
            raise SmsParseException("Not SMS protocol, bailing")

        # get and interpet DCS (char encoding info)
        self.encoding,pdu=_consume(pdu,1,_read_dcs)
        if self.encoding not in ['gsm','ucs2']:
            raise SmsParseException("Don't understand short message encoding")

        #get and interpret timestamp
        self.sent_ts,pdu=_consume(pdu,7,_read_ts)

        # ok, how long is ud? 
        # note, if encoding is GSM this is num 7-bit septets
        # if ucs2, it's num bytes
        udl,pdu=_consume_bytes(pdu,1)

        # Now to deal with the User Data header!
        if tp_udhi:
            # yup, we got one, probably part of a 'concatenated short message',
            # what happens when you type too much text and your phone sends
            # multiple SMSs
            #
            # in fact this is the _only_ case we care about
            
            # get the header length
            udhl,pdu=_consume_decimal(pdu)
            
            # now loop through consuming the header
            # and looking to see if we are a csm
            i=0
            while i<udhl:
                # get info about the element
                ie_type,pdu=_consume_bytes(pdu,1)
                ie_l,pdu=_consume_decimal(pdu) 
                ie_d,pdu=_consume(pdu,ie_l)
                i+=(ie_l+2) # move index up for all bytes read
                if ie_type == 0x00:
                    # got csm info!
                    self.is_csm=True
                    (ref,self.csm_total,self.csm_seq),r=_consume_bytes(ie_d,3)
                    self.csm_ref=ref % 256 # the definition is 'modulo 256'
        # ok, done with header

        # now see if we are gsm, in which case we need to unpack bits
        if self.encoding=='gsm':
            # if we had a data header, we need to figure out padding
            if tp_udhi:
                # num septets * 7 bits minus
                # 8 * header length (+1 for length indicator octet)
                # mod'd by 7 to git the number of leftover padding bits
                padding=((7*udl) - (8*(udhl+1))) % 7
            else:
               padding=0

            # now decode
            self.text=_unpack_septets(pdu, padding).decode('gsm')

        else:
            # we are just good old UCS2
            # problem is, we don't necessarily know the byte order
            # some phones include it, some--including some
            # popular Nokia's _don't_, in which case it
            # seems they use big-endian...
        
            bom=pdu[0:4]
            if bom==codecs.BOM_UTF16_LE.encode('hex') or \
                    bom==codecs.BOM_UTF16_BE.encode('hex'):
                codec='utf_16' # which will read the BOM
            else:
                codec='utf_16_be' # which will assume no BOM and big-endian
        
            self.text=pdu.decode('hex').decode(codec)

        # some phones add a leading <cr> so strip it
        self.text=self.text.strip()

#
# And all the ugly helper functions
#

def _read_dcs(dcs):
    # make an int for masking
    dcs=int(dcs,16)

    # for an SMS, as opposed to a 'voice mail waiting'
    # indicator, first 4-bits must be zero
    if dcs & 0xf0 != 0:
        # not an SMS!
        return None

    dcs &= 0x0c # mask off everything but bits 3&2
    if dcs==0:
        return 'gsm'
    elif dcs==8:
        return 'ucs2'

    # not a type we know about, but should never get here
    return None

def _B(slot):
    """Convert slot to Byte boundary"""
    return slot*2

def _consume(seq, num,func=None):
    """
    Consume the num of BYTES

    return a tuple of (consumed,remainder)

    func -- a function to call on the consumed. Result in tuple[0]
    
    """
    num=_B(num)
    c=seq[:num]
    r=seq[num:]
    if func:
        c=func(c)
    return (c,r)

def _consume_decimal(seq):
    """read 2 chars as a decimal"""
    return (int(seq[0:2],10),seq[2:])
    
def _consume_bytes(seq,num=1):
    """
    consumes bytes for num ints (e.g. 2-chars per byte)
    coverts to int, returns tuple of  ([byte...], remainder)

    Special case, if num==1, returns (int, remainder)
       
    """
    
    bytes=[]
    for i in range(0,_B(num),2):
        bytes.append(int(seq[i:i+2],16))
    
    if len(bytes)==1:
        bytes=bytes[0]
    return (bytes,seq[_B(num):])

def _twiddle(seq, decode=True):
    seq=seq.lower() # just in case
    result=list()
    for i in range(0,len(seq)-1,2):
        result.extend((seq[i+1],seq[i]))
    
    if decode and result[-1:][0]=='f':
        # strip trailing 'f'
        result.pop()
    else:
        # check to see if need to _add_ trailing f
        # and since we are already twiddled, it 
        # goes as second to last
        if len(result) % 2 != 0:
            # we're odd, so pad with 'f'
            result.insert(len(result)-1,'f')

    return ''.join(result)

def _parse_phone_num(num_type,seq):
    # sender number is encoded in DECIMAL with each octect swapped, and 
    # padded to even length with F
    # so 1 415 555 1212 is: 41 51 55 15 12 f2
    num=_twiddle(seq)
    
    intl_code=''
    if num_type[0]=='9':
        intl_code='+'
    return '%s%s' % (intl_code,num)

def _chop(seq,how_much):
    """chops the number of octets given off front of seq"""
    return seq[_B(how_much):]

TS_MATCHER=re.compile(r'^(..)(..)(..)(..)(..)(..)(..)$')
TZ_SIGN_MASK=0x08

def _read_ts(seq):
    ts=_twiddle(seq)
    yr,mo,dy,hr,mi,se,tz=[int(g) for g in TS_MATCHER.match(ts).groups()]

    # year is 2 digit! Yeah! Y2K problem again!!
    if yr<90:
        yr+=2000
    else:
        yr+=1900

    # TZ is 15 minute +/- delta from GMT. Lets figure out
    # if we are + or -
    if tz>0x80:
        tz=-(tz-0x80)
    tz_offset=tz/4

    # python sucks with timezones, 
    # so create UTC not using this offset
    dt_local=datetime.datetime(yr,mo,dy,hr,mi,se, tzinfo=pytz.utc)    

    # now add the delta--so we have a UTC time adjusted for the inbound info
    return dt_local+datetime.timedelta(hours=tz_offset)

def _to_binary(n):
    s = ""
    for i in range(8):
        s = ("%1d" % (n & 1)) + s
        n >>= 1
    return s

def _unpack_septets(seq,padding=0):
    """ 
    this function taken from:
    http://offog.org/darcs/misccode/desms.py

    Thank you Adam Sampson <ats@offog.org>!
    """

    # Unpack 7-bit characters
    msgbytes,r = _consume_bytes(seq,len(seq)/2)
    msgbytes.reverse()
    asbinary = ''.join(map(_to_binary, msgbytes))
    if padding != 0:
        asbinary = asbinary[:-padding]
    chars = []
    while len(asbinary) >= 7:
        chars.append(int(asbinary[-7:], 2))
        asbinary = asbinary[:-7]
    return "".join(map(chr, chars))

def _pack_septets(in_bytes, padding=0):
    bytes=[]
    bytes.extend(in_bytes)
    bytes.reverse()
    asbinary = ''.join([_to_binary(b)[1:] for b in bytes])
    # add padding
    for i in range(padding):
        asbinary+='0'
    
    # zero extend last octet if needed
    extra = len(asbinary) % 8
    if extra>0:
        for i in range(8-extra):
            asbinary='0'+asbinary
        
    # convert back to bytes
    bytes=[]
    for i in range(0,len(asbinary),8):
        bytes.append(int(asbinary[i:i+8],2))
    bytes.reverse()
    return bytes

if __name__ == "__main__":
    # poor man's unit tests
    
    pdus = [
        "0791227167830001040C912271271640910008906012024514001C002E004020AC00A300680065006C006C006F002000E900EC006B00F0",
        "07917283010010F5040BC87238880900F10000993092516195800AE8329BFD4697D9EC37",
        "0791448720900253040C914497035290960000500151614414400DD4F29C9E769F41E17338ED06",
        "0791448720003023440C91449703529096000050015132532240A00500037A020190E9339A9D3EA3E920FA1B1466B341E472193E079DD3EE73D85DA7EB41E7B41C1407C1CBF43228CC26E3416137390F3AABCFEAB3FAAC3EABCFEAB3FAAC3EABCFEAB3FAAC3EABCFEAB3FADC3EB7CFED73FBDC3EBF5D4416D9457411596457137D87B7E16438194E86BBCF6D16D9055D429548A28BE822BA882E6370196C2A8950E291E822BA88",
        "0791448720003023440C91449703529096000050015132537240310500037A02025C4417D1D52422894EE5B17824BA8EC423F1483C129BC725315464118FCDE011247C4A8B44",
        "07914477790706520414D06176198F0EE361F2321900005001610013334014C324350B9287D12079180D92A3416134480E",
        "0791448720003023440C91449703529096000050016121855140A005000301060190F5F31C447F83C8E5327CEE0221EBE73988FE0691CB65F8DC05028190F5F31C447F83C8E5327CEE028140C8FA790EA2BF41E472193E7781402064FD3C07D1DF2072B90C9FBB402010B27E9E83E86F10B95C86CF5D2064FD3C07D1DF2072B90C9FBB40C8FA790EA2BF41E472193E7781402064FD3C07D1DF2072B90C9FBB402010B27E9E83E8",
         "0791448720003023440C91449703529096000050016121850240A0050003010602DE2072B90C9FBB402010B27E9E83E86F10B95C86CF5D201008593FCF41F437885C2EC3E72E100884AC9FE720FA1B442E97E1731708593FCF41F437885C2EC3E72E100884AC9FE720FA1B442E97E17317080442D6CF7310FD0D2297CBF0B90B040221EBE73988FE0691CB65F8DC05028190F5F31C447F83C8E5327CEE028140C8FA790EA2BF41",
        "0791448720003023440C91449703529096000050016121854240A0050003010603C8E5327CEE0221EBE73988FE0691CB65F8DC05028190F5F31C447F83C8E5327CEE028140C8FA790EA2BF41E472193E7781402064FD3C07D1DF2072B90C9FBB402010B27E9E83E86F10B95C86CF5D201008593FCF41F437885C2EC3E72E10B27E9E83E86F10B95C86CF5D201008593FCF41F437885C2EC3E72E100884AC9FE720FA1B442E97E1",
        "0791448720003023400C91449703529096000050016121858240A0050003010604E62E100884AC9FE720FA1B442E97E17317080442D6CF7310FD0D2297CBF0B90B040221EBE73988FE0691CB65F8DC0542D6CF7310FD0D2297CBF0B90B040221EBE73988FE0691CB65F8DC05028190F5F31C447F83C8E5327CEE028140C8FA790EA2BF41E472193E7781402064FD3C07D1DF2072B90C9FBB402010B27E9E83E86F10B95C86CF5D",
        "0791448720003023400C91449703529096000050016121853340A005000301060540C8FA790EA2BF41E472193E7781402064FD3C07D1DF2072B90C9FBB402010B27E9E83E86F10B95C86CF5D201008593FCF41F437885C2EC3E72E100884AC9FE720FA1B442E97E17317080442D6CF7310FD0D2297CBF0B90B84AC9FE720FA1B442E97E17317080442D6CF7310FD0D2297CBF0B90B040221EBE73988FE0691CB65F8DC05028190",
        "0791448720003023440C914497035290960000500161218563402A050003010606EAE73988FE0691CB65F8DC05028190F5F31C447F83C8E5327CEE0281402010",
        ]

    for p in pdus:
        print GsmPdu(p).dump()




