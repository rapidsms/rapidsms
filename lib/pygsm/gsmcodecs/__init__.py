# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

#
# Codec registry functions
#

import codecs
import gsm0338

#constants
ALIASES=['gsm','gsm0338']
GSM_CODEC_ENTRY='gsm_codec_entry'

#module globals
_G={ 
    GSM_CODEC_ENTRY:None
}

def search_function(encoding):
    if encoding not in ALIASES:
        return None

    if _G[GSM_CODEC_ENTRY] is None:
        _G[GSM_CODEC_ENTRY]=gsm0338.getregentry()

    return _G[GSM_CODEC_ENTRY]
        
codecs.register(search_function)
