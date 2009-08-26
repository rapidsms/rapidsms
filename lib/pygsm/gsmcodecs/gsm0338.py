# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

""" Python Character Mapping Codec based on gsm0338 generated from './GSM0338.TXT' with gencodec.py.
    
    With extra sauce to deal with the 'multibyte' extensions!

"""#"

import codecs
import re

### Codec APIs

#
# Shared funcs
#
def _encode(input,errors='strict'):
    # split to see if we have any 'extended' characters
    runs=unicode_splitter.split(input)
    
    # now iterate through handling any 'multibyte' ourselves
    out_str=list()
    consumed=0
    extended=extended_encode_map.keys()
    for run in runs:
        if len(run)==1 and run[0] in extended:
            out_str.append(extended_indicator+extended_encode_map[run])
            consumed+=1
        else:
            # pass it to the standard encoder
            out,cons=codecs.charmap_encode(run,errors,encoding_table)
            out_str.append(out)
            consumed+=cons
    return (''.join(out_str),consumed)

def _decode(input,errors='strict'):
    # opposite of above, look for multibye 'marker'
    # and handle it ourselves, pass the rest to the
    # standard decoder
    
    # split to see if we have any 'extended' characters
    runs = str_splitter.split(input)

    # now iterate through handling any 'multibyte' ourselves
    out_uni = []
    consumed = 0
    for run in runs:
        if len(run)==0:
            # first char was a marker, but we don't care
            # the marker itself will come up in the next run
            continue
        if len(run)==2 and run[0]==extended_indicator:
            try:
                out_uni.append(extended_decode_map[run[1]])
                consumed += 2
                continue
            except KeyError:
                # second char was not an extended, so
                # let this pass through and the marker
                # will be interpreted by the table as a NBSP
                pass

        # pass it to the standard encoder
        out,cons=codecs.charmap_decode(run,errors,decoding_table)
        out_uni.append(out)
        consumed+=cons
    return (u''.join(out_uni),consumed)


class Codec(codecs.Codec):
    def encode(self,input,errors='strict'):
        return _encode(input,errors)

    def decode(self,input,errors='strict'):
        # strip any trailing '\x00's as the standard
        # says trailing ones are _not_ @'s and 
        # are in fact blanks
        if input[-1]=='\x00':
            input=input[:-1]
        return _decode(input,errors)

class IncrementalEncoder(codecs.IncrementalEncoder):
    def encode(self, input, final=False):
        # just use the standard encoding as there is no need
        # to hold state
        return _encode(input,self.errors)[0]

class IncrementalDecoder(codecs.IncrementalDecoder):
    # a little trickier 'cause input _might_ come in
    # split right on the extended char marker boundary
    def __init__(self,errors='strict'):
        codecs.IncrementalDecoder.__init__(self,errors)
        self.last_saw_mark=False

    def decode(self, input, final=False):
        if final:
            # check for final '\x00' which should not
            # be interpreted as a '@'
            if input[-1]=='\x00':
                input=input[:-1]

        # keep track of how many chars we've added or
        # removed to the run to adjust the response from
        # _decode
        consumed_delta=0
        # see if last char was a 2-byte mark
        if self.last_saw_mark:
            # add it back to the current run
            input=extended_indicator+input
            consumed_delta-=1 # 'cause we added a char
            self.last_saw_mark=False # reset
        if input[-1:]==extended_indicator and not final:
            # chop it off
            input=input[:-1]
            consumed_delta+=1 # because we just consumed one char
            self.last_saw_mark=True

            # NOTE: if we are final and last mark is 
            # and extended indicator, it will be interpreted
            # as NBSP
        return _decode(input,self.errors)[0]

    def reset(self):
        self.last_saw_mark=False

class StreamWriter(Codec,codecs.StreamWriter):
    pass

class StreamReader(Codec,codecs.StreamReader):
    pass

### encodings module API

def getregentry():
    return codecs.CodecInfo(
        name='gsm0338',
        encode=Codec().encode,
        decode=Codec().decode,
        incrementalencoder=IncrementalEncoder,
        incrementaldecoder=IncrementalDecoder,
        streamreader=StreamReader,
        streamwriter=StreamWriter,
    )


### Decoding Tables

# gsm 'extended' character.
# gsm, annoyingly, is MOSTLY 7-bit chars
#
# BUT has 10 'extended' chars represented
# by 2-chars, an idicator, and then one of 
# the 10

# first of the 2-chars is indicator
extended_indicator='\x1b'

# second char is the 'extended' character
extended_encode_map = { # Unicode->GSM string
    u'\x0c':'\x0a',  # FORM FEED
    u'^':'\x14',     # CIRCUMFLEX ACCENT
    u'{':'\x28',     # LEFT CURLY BRACKET
    u'}':'\x29',     # RIGHT CURLY BRACKET
    u'\\':'\x2f',    # REVERSE SOLIDUS
    u'[':'\x3c',     # LEFT SQUARE BRACKET
    u'~':'\x3d',     # TILDE
    u']':'\x3e',     # RIGHT SQUARE BRACKET
    u'|':'\x40',     # VERTICAL LINE
    u'\u20ac':'\x65' # EURO SIGN
}

# reverse the map above for decoding
# GSM String->Unicode
uni,gsm=zip(*extended_encode_map.items())
extended_decode_map=dict(zip(gsm,uni))

# splitter
str_splitter=re.compile('(%(ind)s[^%(ind)s])' % { 'ind':extended_indicator })
unicode_splitter=re.compile(u'([%s])' % re.escape(''.join(extended_encode_map.keys())), re.UNICODE)

# the normal 1-char table
decoding_table = (
    u'@'        #  0x00 -> COMMERCIAL AT
    u'\xa3'     #  0x01 -> POUND SIGN
    u'$'        #  0x02 -> DOLLAR SIGN
    u'\xa5'     #  0x03 -> YEN SIGN
    u'\xe8'     #  0x04 -> LATIN SMALL LETTER E WITH GRAVE
    u'\xe9'     #  0x05 -> LATIN SMALL LETTER E WITH ACUTE
    u'\xf9'     #  0x06 -> LATIN SMALL LETTER U WITH GRAVE
    u'\xec'     #  0x07 -> LATIN SMALL LETTER I WITH GRAVE
    u'\xf2'     #  0x08 -> LATIN SMALL LETTER O WITH GRAVE
    u'\xe7'     #  0x09 -> LATIN SMALL LETTER C WITH CEDILLA
    u'\n'       #  0x0A -> LINE FEED
    u'\xd8'     #  0x0B -> LATIN CAPITAL LETTER O WITH STROKE
    u'\xf8'     #  0x0C -> LATIN SMALL LETTER O WITH STROKE
    u'\r'       #  0x0D -> CARRIAGE RETURN
    u'\xc5'     #  0x0E -> LATIN CAPITAL LETTER A WITH RING ABOVE
    u'\xe5'     #  0x0F -> LATIN SMALL LETTER A WITH RING ABOVE
    u'\u0394'   #  0x10 -> GREEK CAPITAL LETTER DELTA
    u'_'        #  0x11 -> LOW LINE
    u'\u03a6'   #  0x12 -> GREEK CAPITAL LETTER PHI
    u'\u0393'   #  0x13 -> GREEK CAPITAL LETTER GAMMA
    u'\u039b'   #  0x14 -> GREEK CAPITAL LETTER LAMDA
    u'\u03a9'   #  0x15 -> GREEK CAPITAL LETTER OMEGA
    u'\u03a0'   #  0x16 -> GREEK CAPITAL LETTER PI
    u'\u03a8'   #  0x17 -> GREEK CAPITAL LETTER PSI
    u'\u03a3'   #  0x18 -> GREEK CAPITAL LETTER SIGMA
    u'\u0398'   #  0x19 -> GREEK CAPITAL LETTER THETA
    u'\u039e'   #  0x1A -> GREEK CAPITAL LETTER XI
    u'\xa0'     #  0x1B -> ESCAPE TO EXTENSION TABLE (or displayed as NBSP, see note above)
    u'\xc6'     #  0x1C -> LATIN CAPITAL LETTER AE
    u'\xe6'     #  0x1D -> LATIN SMALL LETTER AE
    u'\xdf'     #  0x1E -> LATIN SMALL LETTER SHARP S (German)
    u'\xc9'     #  0x1F -> LATIN CAPITAL LETTER E WITH ACUTE
    u' '        #  0x20 -> SPACE
    u'!'        #  0x21 -> EXCLAMATION MARK
    u'"'        #  0x22 -> QUOTATION MARK
    u'#'        #  0x23 -> NUMBER SIGN
    u'\xa4'     #  0x24 -> CURRENCY SIGN
    u'%'        #  0x25 -> PERCENT SIGN
    u'&'        #  0x26 -> AMPERSAND
    u"'"        #  0x27 -> APOSTROPHE
    u'('        #  0x28 -> LEFT PARENTHESIS
    u')'        #  0x29 -> RIGHT PARENTHESIS
    u'*'        #  0x2A -> ASTERISK
    u'+'        #  0x2B -> PLUS SIGN
    u','        #  0x2C -> COMMA
    u'-'        #  0x2D -> HYPHEN-MINUS
    u'.'        #  0x2E -> FULL STOP
    u'/'        #  0x2F -> SOLIDUS
    u'0'        #  0x30 -> DIGIT ZERO
    u'1'        #  0x31 -> DIGIT ONE
    u'2'        #  0x32 -> DIGIT TWO
    u'3'        #  0x33 -> DIGIT THREE
    u'4'        #  0x34 -> DIGIT FOUR
    u'5'        #  0x35 -> DIGIT FIVE
    u'6'        #  0x36 -> DIGIT SIX
    u'7'        #  0x37 -> DIGIT SEVEN
    u'8'        #  0x38 -> DIGIT EIGHT
    u'9'        #  0x39 -> DIGIT NINE
    u':'        #  0x3A -> COLON
    u';'        #  0x3B -> SEMICOLON
    u'<'        #  0x3C -> LESS-THAN SIGN
    u'='        #  0x3D -> EQUALS SIGN
    u'>'        #  0x3E -> GREATER-THAN SIGN
    u'?'        #  0x3F -> QUESTION MARK
    u'\xa1'     #  0x40 -> INVERTED EXCLAMATION MARK
    u'A'        #  0x41 -> LATIN CAPITAL LETTER A
    u'B'        #  0x42 -> LATIN CAPITAL LETTER B
    u'C'        #  0x43 -> LATIN CAPITAL LETTER C
    u'D'        #  0x44 -> LATIN CAPITAL LETTER D
    u'E'        #  0x45 -> LATIN CAPITAL LETTER E
    u'F'        #  0x46 -> LATIN CAPITAL LETTER F
    u'G'        #  0x47 -> LATIN CAPITAL LETTER G
    u'H'        #  0x48 -> LATIN CAPITAL LETTER H
    u'I'        #  0x49 -> LATIN CAPITAL LETTER I
    u'J'        #  0x4A -> LATIN CAPITAL LETTER J
    u'K'        #  0x4B -> LATIN CAPITAL LETTER K
    u'L'        #  0x4C -> LATIN CAPITAL LETTER L
    u'M'        #  0x4D -> LATIN CAPITAL LETTER M
    u'N'        #  0x4E -> LATIN CAPITAL LETTER N
    u'O'        #  0x4F -> LATIN CAPITAL LETTER O
    u'P'        #  0x50 -> LATIN CAPITAL LETTER P
    u'Q'        #  0x51 -> LATIN CAPITAL LETTER Q
    u'R'        #  0x52 -> LATIN CAPITAL LETTER R
    u'S'        #  0x53 -> LATIN CAPITAL LETTER S
    u'T'        #  0x54 -> LATIN CAPITAL LETTER T
    u'U'        #  0x55 -> LATIN CAPITAL LETTER U
    u'V'        #  0x56 -> LATIN CAPITAL LETTER V
    u'W'        #  0x57 -> LATIN CAPITAL LETTER W
    u'X'        #  0x58 -> LATIN CAPITAL LETTER X
    u'Y'        #  0x59 -> LATIN CAPITAL LETTER Y
    u'Z'        #  0x5A -> LATIN CAPITAL LETTER Z
    u'\xc4'     #  0x5B -> LATIN CAPITAL LETTER A WITH DIAERESIS
    u'\xd6'     #  0x5C -> LATIN CAPITAL LETTER O WITH DIAERESIS
    u'\xd1'     #  0x5D -> LATIN CAPITAL LETTER N WITH TILDE
    u'\xdc'     #  0x5E -> LATIN CAPITAL LETTER U WITH DIAERESIS
    u'\xa7'     #  0x5F -> SECTION SIGN
    u'\xbf'     #  0x60 -> INVERTED QUESTION MARK
    u'a'        #  0x61 -> LATIN SMALL LETTER A
    u'b'        #  0x62 -> LATIN SMALL LETTER B
    u'c'        #  0x63 -> LATIN SMALL LETTER C
    u'd'        #  0x64 -> LATIN SMALL LETTER D
    u'e'        #  0x65 -> LATIN SMALL LETTER E
    u'f'        #  0x66 -> LATIN SMALL LETTER F
    u'g'        #  0x67 -> LATIN SMALL LETTER G
    u'h'        #  0x68 -> LATIN SMALL LETTER H
    u'i'        #  0x69 -> LATIN SMALL LETTER I
    u'j'        #  0x6A -> LATIN SMALL LETTER J
    u'k'        #  0x6B -> LATIN SMALL LETTER K
    u'l'        #  0x6C -> LATIN SMALL LETTER L
    u'm'        #  0x6D -> LATIN SMALL LETTER M
    u'n'        #  0x6E -> LATIN SMALL LETTER N
    u'o'        #  0x6F -> LATIN SMALL LETTER O
    u'p'        #  0x70 -> LATIN SMALL LETTER P
    u'q'        #  0x71 -> LATIN SMALL LETTER Q
    u'r'        #  0x72 -> LATIN SMALL LETTER R
    u's'        #  0x73 -> LATIN SMALL LETTER S
    u't'        #  0x74 -> LATIN SMALL LETTER T
    u'u'        #  0x75 -> LATIN SMALL LETTER U
    u'v'        #  0x76 -> LATIN SMALL LETTER V
    u'w'        #  0x77 -> LATIN SMALL LETTER W
    u'x'        #  0x78 -> LATIN SMALL LETTER X
    u'y'        #  0x79 -> LATIN SMALL LETTER Y
    u'z'        #  0x7A -> LATIN SMALL LETTER Z
    u'\xe4'     #  0x7B -> LATIN SMALL LETTER A WITH DIAERESIS
    u'\xf6'     #  0x7C -> LATIN SMALL LETTER O WITH DIAERESIS
    u'\xf1'     #  0x7D -> LATIN SMALL LETTER N WITH TILDE
    u'\xfc'     #  0x7E -> LATIN SMALL LETTER U WITH DIAERESIS
    u'\xe0'     #  0x7F -> LATIN SMALL LETTER A WITH GRAVE
    u'\ufffe'   #  0x80 -> UNDEFINED
    u'\ufffe'   #  0x81 -> UNDEFINED
    u'\ufffe'   #  0x82 -> UNDEFINED
    u'\ufffe'   #  0x83 -> UNDEFINED
    u'\ufffe'   #  0x84 -> UNDEFINED
    u'\ufffe'   #  0x85 -> UNDEFINED
    u'\ufffe'   #  0x86 -> UNDEFINED
    u'\ufffe'   #  0x87 -> UNDEFINED
    u'\ufffe'   #  0x88 -> UNDEFINED
    u'\ufffe'   #  0x89 -> UNDEFINED
    u'\ufffe'   #  0x8A -> UNDEFINED
    u'\ufffe'   #  0x8B -> UNDEFINED
    u'\ufffe'   #  0x8C -> UNDEFINED
    u'\ufffe'   #  0x8D -> UNDEFINED
    u'\ufffe'   #  0x8E -> UNDEFINED
    u'\ufffe'   #  0x8F -> UNDEFINED
    u'\ufffe'   #  0x90 -> UNDEFINED
    u'\ufffe'   #  0x91 -> UNDEFINED
    u'\ufffe'   #  0x92 -> UNDEFINED
    u'\ufffe'   #  0x93 -> UNDEFINED
    u'\ufffe'   #  0x94 -> UNDEFINED
    u'\ufffe'   #  0x95 -> UNDEFINED
    u'\ufffe'   #  0x96 -> UNDEFINED
    u'\ufffe'   #  0x97 -> UNDEFINED
    u'\ufffe'   #  0x98 -> UNDEFINED
    u'\ufffe'   #  0x99 -> UNDEFINED
    u'\ufffe'   #  0x9A -> UNDEFINED
    u'\ufffe'   #  0x9B -> UNDEFINED
    u'\ufffe'   #  0x9C -> UNDEFINED
    u'\ufffe'   #  0x9D -> UNDEFINED
    u'\ufffe'   #  0x9E -> UNDEFINED
    u'\ufffe'   #  0x9F -> UNDEFINED
    u'\ufffe'   #  0xA0 -> UNDEFINED
    u'\ufffe'   #  0xA1 -> UNDEFINED
    u'\ufffe'   #  0xA2 -> UNDEFINED
    u'\ufffe'   #  0xA3 -> UNDEFINED
    u'\ufffe'   #  0xA4 -> UNDEFINED
    u'\ufffe'   #  0xA5 -> UNDEFINED
    u'\ufffe'   #  0xA6 -> UNDEFINED
    u'\ufffe'   #  0xA7 -> UNDEFINED
    u'\ufffe'   #  0xA8 -> UNDEFINED
    u'\ufffe'   #  0xA9 -> UNDEFINED
    u'\ufffe'   #  0xAA -> UNDEFINED
    u'\ufffe'   #  0xAB -> UNDEFINED
    u'\ufffe'   #  0xAC -> UNDEFINED
    u'\ufffe'   #  0xAD -> UNDEFINED
    u'\ufffe'   #  0xAE -> UNDEFINED
    u'\ufffe'   #  0xAF -> UNDEFINED
    u'\ufffe'   #  0xB0 -> UNDEFINED
    u'\ufffe'   #  0xB1 -> UNDEFINED
    u'\ufffe'   #  0xB2 -> UNDEFINED
    u'\ufffe'   #  0xB3 -> UNDEFINED
    u'\ufffe'   #  0xB4 -> UNDEFINED
    u'\ufffe'   #  0xB5 -> UNDEFINED
    u'\ufffe'   #  0xB6 -> UNDEFINED
    u'\ufffe'   #  0xB7 -> UNDEFINED
    u'\ufffe'   #  0xB8 -> UNDEFINED
    u'\ufffe'   #  0xB9 -> UNDEFINED
    u'\ufffe'   #  0xBA -> UNDEFINED
    u'\ufffe'   #  0xBB -> UNDEFINED
    u'\ufffe'   #  0xBC -> UNDEFINED
    u'\ufffe'   #  0xBD -> UNDEFINED
    u'\ufffe'   #  0xBE -> UNDEFINED
    u'\ufffe'   #  0xBF -> UNDEFINED
    u'\ufffe'   #  0xC0 -> UNDEFINED
    u'\ufffe'   #  0xC1 -> UNDEFINED
    u'\ufffe'   #  0xC2 -> UNDEFINED
    u'\ufffe'   #  0xC3 -> UNDEFINED
    u'\ufffe'   #  0xC4 -> UNDEFINED
    u'\ufffe'   #  0xC5 -> UNDEFINED
    u'\ufffe'   #  0xC6 -> UNDEFINED
    u'\ufffe'   #  0xC7 -> UNDEFINED
    u'\ufffe'   #  0xC8 -> UNDEFINED
    u'\ufffe'   #  0xC9 -> UNDEFINED
    u'\ufffe'   #  0xCA -> UNDEFINED
    u'\ufffe'   #  0xCB -> UNDEFINED
    u'\ufffe'   #  0xCC -> UNDEFINED
    u'\ufffe'   #  0xCD -> UNDEFINED
    u'\ufffe'   #  0xCE -> UNDEFINED
    u'\ufffe'   #  0xCF -> UNDEFINED
    u'\ufffe'   #  0xD0 -> UNDEFINED
    u'\ufffe'   #  0xD1 -> UNDEFINED
    u'\ufffe'   #  0xD2 -> UNDEFINED
    u'\ufffe'   #  0xD3 -> UNDEFINED
    u'\ufffe'   #  0xD4 -> UNDEFINED
    u'\ufffe'   #  0xD5 -> UNDEFINED
    u'\ufffe'   #  0xD6 -> UNDEFINED
    u'\ufffe'   #  0xD7 -> UNDEFINED
    u'\ufffe'   #  0xD8 -> UNDEFINED
    u'\ufffe'   #  0xD9 -> UNDEFINED
    u'\ufffe'   #  0xDA -> UNDEFINED
    u'\ufffe'   #  0xDB -> UNDEFINED
    u'\ufffe'   #  0xDC -> UNDEFINED
    u'\ufffe'   #  0xDD -> UNDEFINED
    u'\ufffe'   #  0xDE -> UNDEFINED
    u'\ufffe'   #  0xDF -> UNDEFINED
    u'\ufffe'   #  0xE0 -> UNDEFINED
    u'\ufffe'   #  0xE1 -> UNDEFINED
    u'\ufffe'   #  0xE2 -> UNDEFINED
    u'\ufffe'   #  0xE3 -> UNDEFINED
    u'\ufffe'   #  0xE4 -> UNDEFINED
    u'\ufffe'   #  0xE5 -> UNDEFINED
    u'\ufffe'   #  0xE6 -> UNDEFINED
    u'\ufffe'   #  0xE7 -> UNDEFINED
    u'\ufffe'   #  0xE8 -> UNDEFINED
    u'\ufffe'   #  0xE9 -> UNDEFINED
    u'\ufffe'   #  0xEA -> UNDEFINED
    u'\ufffe'   #  0xEB -> UNDEFINED
    u'\ufffe'   #  0xEC -> UNDEFINED
    u'\ufffe'   #  0xED -> UNDEFINED
    u'\ufffe'   #  0xEE -> UNDEFINED
    u'\ufffe'   #  0xEF -> UNDEFINED
    u'\ufffe'   #  0xF0 -> UNDEFINED
    u'\ufffe'   #  0xF1 -> UNDEFINED
    u'\ufffe'   #  0xF2 -> UNDEFINED
    u'\ufffe'   #  0xF3 -> UNDEFINED
    u'\ufffe'   #  0xF4 -> UNDEFINED
    u'\ufffe'   #  0xF5 -> UNDEFINED
    u'\ufffe'   #  0xF6 -> UNDEFINED
    u'\ufffe'   #  0xF7 -> UNDEFINED
    u'\ufffe'   #  0xF8 -> UNDEFINED
    u'\ufffe'   #  0xF9 -> UNDEFINED
    u'\ufffe'   #  0xFA -> UNDEFINED
    u'\ufffe'   #  0xFB -> UNDEFINED
    u'\ufffe'   #  0xFC -> UNDEFINED
    u'\ufffe'   #  0xFD -> UNDEFINED
    u'\ufffe'   #  0xFE -> UNDEFINED
    u'\ufffe'   #  0xFF -> UNDEFINED
)

encoding_table=codecs.charmap_build(decoding_table)


if __name__ == "__main__":
    """
    Run this as a script for poor-man's unit tests

    """
    isoLatin15_alpha=u" !\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJLKMNOPQRSTUVWXYZ[\\]^-`abcdefghijklmnopqrstuvwxyz{|}~¡¢£€¥Š§š©ª«¬®¯°±²³Žµ¶·ž¹º»ŒœŸ¿ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖ×ØÙÚÛÜÝÞßàáâãäåæçèéêëìíîïðñòóôõö÷øùúûüýþÿ"

    gsm_alpha=u"\u00A0@£$¥èéùìòçØøÅåΔ_ΦΓΛΩΠΨΣΘΞ^{}\\[~]|\u00A0\u00A0€ÆæßÉ !\"#¤%&'()*+,-./0123456789:;<=>?¡ABCDEFGHIJKLMNOPQRSTUVWXYZÄÖÑÜ§¿abcdefghijklmnopqrstuvwxyzäöñüà\u00A0"

    gsm_alpha_encoded='1b000102030405060708090b0c0e0f101112131415161718191a1b141b281b291b2f1b3c1b3d1b3e1b401b1b1b651c1d1e1f202122232425262728292a2b2c2d2e2f303132333435363738393a3b3c3d3e3f404142434445464748494a4b4c4d4e4f505152535455565758595a5b5c5d5e5f606162636465666768696a6b6c6d6e6f707172737475767778797a7b7c7d7e7f1b'

    gsm_alpha_gsm=gsm_alpha_encoded.decode('hex')


    # some simple tests
    print "Assert GSM alphabet, encoded in GSM is correct (unicode->gsm_str)..."
    encoded=_encode(gsm_alpha)[0].encode('hex')
    print encoded
    assert(encoded==gsm_alpha_encoded)
    print "Good"
    print
    print "Assert GSM encoded string converts to correct Unicode (gsm_str->unicode)..."
    assert(_decode(gsm_alpha_gsm)[0]==gsm_alpha)
    print "Good"
    print

    # test Codec objects
    print "Try the codec objects unicode_test_str->encode->decode==unicode_test_str..."
    c=Codec()
    gsm_str,out=c.encode(gsm_alpha)
    assert(c.decode(gsm_str)[0]==gsm_alpha)
    print "Good"
    print
    print "Try the incremental codecs, same test, but loop it..."

    def _inc_encode(ie):
        encoded=list()
        hop=17 # make it something odd
        final=False
        for i in range(0,len(gsm_alpha),hop):
            end=i+hop
            if end>=len(gsm_alpha): final=True
            encoded.append(ie.encode(gsm_alpha[i:end],final))
        return ''.join(encoded)

    enc=IncrementalEncoder()            
    assert(_inc_encode(enc)==gsm_alpha_gsm)
    print "Good"
    print
    print "Now do that again with the same encoder to make sure state is reset..."
    enc.reset()
    assert(_inc_encode(enc)==gsm_alpha_gsm)
    print "Good"
    print
    print "Now decode the encoded string back to unicode..."

    def _inc_decode(idec):
        decoded=list()
        # define so we KNOW we hit a mark as last char
        hop=gsm_alpha_gsm.index('\x1b')+1
        final=False
        for i in range(0,len(gsm_alpha_gsm),hop):
            end=i+hop
            if end>=len(gsm_alpha_gsm): final=True
            decoded.append(idec.decode(gsm_alpha_gsm[i:end],final))
        return ''.join(decoded)

    dec=IncrementalDecoder()
    assert(_inc_decode(dec)==gsm_alpha)
    print "Good"
    print
    print "Do it again with some decoder to make sure state is cleared..."
    dec.reset()
    assert(_inc_decode(dec)==gsm_alpha)
    print "Good"
    print
    
