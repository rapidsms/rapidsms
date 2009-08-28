""" 
Translation Checker

Run this function over translation text files (typically django.po)
and it will check whether they are safe for sms (gsm or UCS-2)
"""

from __future__ import with_statement
import os
import sys
import codecs
import getopt

# hack to get paths working - should use django's runscript instead
CUR_DIR = os.getcwd()
os.chdir('..')
# TODO - change this directory to wherever pygsm ends up
sys.path.append(os.path.join(os.getcwd(),os.path.join('lib')))
import pygsm.gsmcodecs

# attempt to interpret the input file as encodings in this order
# standard codecs are listed here: http://docs.python.org/library/codecs.html
# NOTE: There is no way to accurately identify the character encoding of 
# an unidentified text file, so we just make a best guess
encodings = ['utf-8','cp1252','utf-16']
line_count = 0

def check_gsm_compatible(infile):
    file_name = infile.rsplit(os.sep,1)[1]
    for enc in encodings:
        try: 
            if can_gsm_encode(enc, infile):
                print "PASSES gsm encoding (%s). File parsed as %s" % (file_name,enc)
                break
        except UnicodeEncodeError, e:
            print "FAILS GSM ENCODING (%s)! (file was read as type %s)" % (file_name,enc)
            print "  Failed on line %d" % line_count
            print "  " + str(e)
            break
    return

def can_gsm_encode(encoding,file_name): 
    """ 
    Tests to see whether this message is gsm-compatible (text-message-worthy)
   
    Returns true if the file could be encoded in gsm with no exceptions thrown
    Returns false if 'encoding' was the wrong encoding for the given file
    Raises UnicodeEncodeError if there is a non-gsm character in the given file
    encoding: the encoding of the input file
    file_name: the file to process

    """
    global line_count
    line_count = 0
    try:
        # first assume we are getting utf-8 encoding (linux default)
        with codecs.open(file_name,'r', encoding=encoding) as fin:
            for line in fin:
                line_count = line_count+1
                line.encode('gsm')
        return True
    except UnicodeDecodeError, e:
        """ This happen when the input file is not of type 'encoding' """
        print "  Cannot parse file as " + encoding
        return False

def main():
    """ Generic wrapper for python scripts """
    try:
        opts, args = getopt.getopt(sys.argv[1:], "h", ["help"])
    except getopt.error, msg:
        print msg
        print "for help use --help"
        sys.exit(2)
    # process options
    for o, a in opts:
        if o in ("-h", "--help"):
            print __doc__
            sys.exit(0)
    # process arguments
    if len(args) < 1:
        print "ERROR: I need at least 1 argument"
    for arg in args:
        infile = os.path.join(CUR_DIR,arg)
        check_gsm_compatible(infile) # process() is defined elsewhere

if __name__ == "__main__":
    main()


