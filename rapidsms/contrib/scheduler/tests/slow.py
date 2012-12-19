""" the slowest set of tests 

tests that a schedule set to fire every minute 
actually does, without speedup
"""

import time
import logging
from datetime import datetime, timedelta
from rapidsms.tests.scripted import TestScript
import rapidsms.contrib.scheduler.app as scheduler_app
from rapidsms.contrib.scheduler.models import EventSchedule, ALL

class TestSlow (TestScript):
    apps = ([scheduler_app.App])
    
    def setUp(self):
        global callback_counter
        callback_counter = 0
        TestScript.setUp(self)
        EventSchedule.objects.all().delete()
        
    def test_one_shot(self):
        """ Test scheduler in real time"""
        global callback_counter
        self.router.start()
        schedule = EventSchedule(callback="scheduler.tests.slow.callback_func", 
                                 minutes=ALL, callback_args=([3]))
        schedule.save()
        time.sleep(180.0)
        self.assertEquals(callback_counter,9)
        self.router.stop()

def callback_func(router, arg):
    global callback_counter
    print "adding %s to global_var (%s)" % (arg, callback_counter)
    logging.info("adding %s to global_var (%s)" % (arg, callback_counter))
    callback_counter = callback_counter + arg
