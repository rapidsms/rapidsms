""" Translation Checker

Run this function with various utf-8 tranlsation files (typically *.po from gettext)
and it will check whether they can be gsm-encoded
"""
from __future__ import with_statement
import sys, os
import codecs
import getopt

# hack to get paths working - we should use django's runscript instead
CUR_DIR = os.getcwd()
os.chdir('..')
sys.path.append(os.path.join(os.getcwd(),os.path.join('lib','pygsm')))

import gsmcodecs

# attempt to interpret the input file in this order
encodings = ['utf-8','cp1252','utf-16']
line_count = 0

def check_gsm_compatible(file):
    file_name = file.rsplit(os.sep,1)[1]
    for enc in encodings:
        try: 
            if can_gsm_encode(enc, file):
                print "PASSES gsm encoding (%s)" % file_name
                break
        except UnicodeEncodeError, e:
            print "FAILS GSM ENCODING (%s)! (file was read as type %s)" % (file_name,enc)
            print "  Failed on line %d" % line_count
            print "  " + str(e)
            break
    return

def can_gsm_encode(encoding,file_name): 
    """ Attempts the gsm conversion and return true if everything is good
        Returns false if 'encoding' was the wrong encoding for the given file
        Raises UnicodeEncodeError if there is a non-gsm character in the given file
        Enc: the encoding of the input file
        File_name: the file to process
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


# generic wrapper for python scripts
def main():
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
        file = os.path.join(CUR_DIR,arg)
        check_gsm_compatible(file) # process() is defined elsewhere

if __name__ == "__main__":
    main()


