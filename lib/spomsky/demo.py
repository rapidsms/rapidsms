#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import time
import spomsky

def callback(source, body):
    print "i was called back by %s: %s" % (source, body)

c = spomsky.Client()
#c.send("sms://3364130840","")
c.subscribe(callback)

# block forever
while True:
    time.sleep(1)
