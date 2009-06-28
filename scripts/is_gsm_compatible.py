""" Translation Checker

Run this function with various tranlsation files (typically *.po from gettext)
and it will check whether they can be gsm-encoded
"""
from __future__ import with_statement
import sys
import os
import io
import codecs

# hack to get paths working - we should use django's runscript instead
CUR_DIR = os.getcwd()
os.chdir('..')
sys.path.append(os.path.join(os.getcwd(),os.path.join('lib','pygsm')))

import getopt
import gsmcodecs

def check_gsm(arg):
    try:
        line_count = 0;
        file_name = os.path.join(CUR_DIR,arg)
        with codecs.open(file_name,'r', encoding='utf-8') as fin:
          for line in fin:
            line.encode('gsm')
            line_count = line_count+1
    except UnicodeEncodeError:
        print "%s does NOT pass gsm encoding!" % arg
        print "failed on line %d" % line_count
        return
    print "%s passes gsm encoding" % arg

def main():
    # parse command line options
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
        check_gsm(arg) # process() is defined elsewhere

if __name__ == "__main__":
    main()


