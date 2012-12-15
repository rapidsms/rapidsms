import time
import logging
from datetime import datetime, timedelta
from rapidsms.tests.scripted import TestScript
import rapidsms.contrib.scheduler.app as scheduler_app
from rapidsms.contrib.scheduler.models import EventSchedule, ALL

class TestSpeedup (TestScript):
    apps = ([scheduler_app.App])
    
    def setUp(self):
        global callback_counter
        callback_counter = 0
        TestScript.setUp(self)
        EventSchedule.objects.all().delete()
        
    def test_one_shot(self):
        """ Basically test 'count'"""
        global callback_counter
        self.router.start()
        # speedup the scheduler so that 1 second == 1 minute
        self.router.get_app('scheduler').schedule_thread._debug_speedup(minutes=1)
        schedule = EventSchedule(callback="scheduler.tests.speedup.callback_func", 
                                 minutes=ALL, callback_args=([3]), count=1)
        schedule.save()
        time.sleep(3.0)
        self.assertEquals(callback_counter,3)
        self.router.stop()
    
    def test_recurring(self):
        """ Test regular recurring schedules """
        global callback_counter
        self.router.start()
        self.router.get_app('scheduler').schedule_thread._debug_speedup(minutes=1)
        schedule = EventSchedule(callback="scheduler.tests.speedup.callback_func", 
                                 minutes=ALL, callback_args=([3]))
        schedule.save()
        time.sleep(2.9)
        self.assertEquals(callback_counter,9)
        self.router.stop()
    
    def test_timestart_timestop(self):
        """ Test timebound schedules """
        global callback_counter
        self.router.start()
        self.router.get_app('scheduler').schedule_thread._debug_speedup(minutes=1)
        start_time = datetime.now() + timedelta(minutes=2)
        end_time = datetime.now() + timedelta(minutes=4)
        schedule = EventSchedule(callback="scheduler.tests.speedup.callback_func", 
                                 minutes=ALL, callback_args=([3]), \
                                 start_time = start_time, end_time = end_time)
        schedule.save()
        time.sleep(7.0)
        self.assertEquals(callback_counter,6)
        self.router.stop()
         
def callback_func(router, arg):
    global callback_counter
    logging.info("adding %s to global_var (%s)" % (arg, callback_counter))
    callback_counter = callback_counter + arg
