#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import sys
import rapidsms
import traceback

print "import server??"
traceback.print_stack()

if __name__ == "__main__":
    
    rapidsms.manager.start(sys.argv)
