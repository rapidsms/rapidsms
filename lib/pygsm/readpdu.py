#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4 encoding=utf8


from __future__ import with_statement

import re, datetime, time
import math
import sys
import serial

pdu='07917283010010F5040BC87238880900F10000993092516195800AE8329BFD4697D9EC37'

PHONE_TYPE_INTL='9'
PHONE_TYPE_NATL='a'
PHONE_TYPE_SUBS='c'
NUM_PLAN_PHONE='1'
NUM_PLAN_TELEX='8'
NUM_PLAN_NATIONAL='f'

# Masks
DCS_COMPRESSED_MASK=0x20
DCS_ENC_MASK=0x0c
DCS_ENC_8_BIT=0x04
DCS_ENC_GSM=0x00
DCS_ENC_UCS2=0x08
DCS_ENC_RESERVED=0x0c

def _read_dcs(dcs):
    coding='gsm'
    compressed=False
    
    # make an int for masking
    dcs=int(dcs,16)

    # special case means default GSM encoding
    if dcs==0:
        return ((coding,compressed))

    if dcs >= 0xf0 : # form 1111 xxxx
        if dcs & DCS_ENC_MASK==DCS_ENC_8_BIT:
            coding='8bit'
    elif dcs <= 0x3ff: # form 00xx xxxx
        compressed=dcs & DCS_COMPRESSED_MASK > 0

        if dcs & DCS_ENC_MASK==DCS_ENC_GSM:
            coding='gsm'
        elif dcs & DCS_ENC_MASK==DCS_ENC_8_BIT:
            coding='8bit'
        elif dcs & DCS_ENC_MASK==DCS_ENC_UCS2:
            coding='utf_16'
        elif dcs & DCS_ENC_MASK==DCS_ENC_RESERVED:
            coding='reserved'
        else:
            # wtf?
            coding=None

    else:
        # not an sms
        return (none,none)

    return((coding,compressed))

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

def _consume_int(seq,digits):
    """consumes digits, coverts to int, returns tuple of  (int, remainder)"""
    def _h_int(val):
        return int(val,16)

    return _consume(seq,digits,_h_int)

def _parse_phone_num(num_type,seq):
    # sender number is encoded in DECIMAL with each octect swapped, and 
    # padded to even length with F
    # so 1 415 555 1212 is: 41 51 55 15 12 f2
    num=list()
    for i in range(0,len(seq)-1,2):
        num.append(seq[i+1])
        if seq[i]!='f':
            num.append(seq[i])

    intl_code=''
    if num_type[0]==PHONE_TYPE_INTL:
        intl_code='+'
    return '%s%s' % (intl_code,''.join(num))

def _chop(seq,how_much):
    """chops the number of octets given off front of seq"""
    return seq[_B(how_much):]

if __name__ == "__main__":
    pdu=pdu.lower()
    print pdu

    # grab smsc header, and throw away
    # length is held in first octet
    smsc_len,pdu=_consume_int(pdu,1)

    # consume smsc header and first byte of deliver
    c,pdu=_consume(pdu, smsc_len+1)

    print pdu

    # send number length is 1 octect in remaining PDU
    sender_dec_len,pdu=_consume_int(pdu,1)

    # length of address is given in _nibbles_ (half octets)
    # convert len to octets, rounding UP if odd
    sender_len=int(math.ceil(sender_dec_len/2.0))

    # next is sender id type
    sender_type,pdu=_consume(pdu,1)

    # now the number itself, (unparsed)
    sender_num,pdu=_consume(pdu,sender_len)

    # now parse
    sender_num=_parse_phone_num(sender_type,sender_num)

    # skip protocol id
    v,pdu=_consume(pdu,1)

    # get and interpet DCS (char encoding info)
    dcs=_consume(pdu,1,_read_dcs)

    #get and interpret timestamp
#    ts=_consume()


    




