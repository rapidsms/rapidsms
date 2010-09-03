#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

"""
NOTE FOR PYGSM USERS: Scheduler launches and runs in a separate thread.
If using it to send scheduled messages with pygsm, make sure pygsm is 
thread-safe.

To use this app, simply create and save EventSchedule instances.
For further details, refer to scheduler.models.py

The following is yet another django-based solution for cron.
What this gives us that other solutions don't seem to (yet) is:
* persistence. all schedules are saved in the db.
* platform-independent
* integration with rapidsms router (doesn't require manually launching
another cron process)
* specification of schedules with minute/hour/day/month granularity, 
including python datetime built-in knowledge of short months, etc.

Other django cron solutions out there include:
http://www.djangosnippets.org/snippets/1348/ - non-persistent, standalone process
http://code.google.com/p/django-cron/ - run_every x seconds
various solutions using linux cron + os.setupenviron
"""

import time
import threading
from datetime import datetime, timedelta

from rapidsms.apps.base import AppBase
from rapidsms.contrib.scheduler.models import EventSchedule

class App (AppBase):
    """ This app provides cron-like functionality for scheduled tasks,
    as defined in the django model EventSchedule
    
    """
    
    bootstrapped = False

    def start (self):
        if not self.bootstrapped:
            # interval to check for scheduled events (in seconds)
            schedule_interval = 60
            # launch scheduling_thread
            self.schedule_thread = SchedulerThread(self.router, schedule_interval)
            self.schedule_thread.start()
            self.bootstrapped = True

    def stop (self):
        self.schedule_thread.stop()

class SchedulerThread (threading.Thread):
    _speedup = None
    
    def __init__ (self, router, schedule_interval):
        super(SchedulerThread, self).__init__(\
            target=self.scheduler_loop,\
            args=(schedule_interval,))
        self.daemon = True
        self._stop = threading.Event()
        self._speedup = None
        self._router = router

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()
    
    def _debug_speedup(self, minutes=0, hours=0, days=0):
        """ This function is purely for the sake of debugging/unit-tests 
        It specifies a time interval in minutes by which the scheduler
        loop jumps ahead. This makes it possible to test long-term intervals
        quickly.
        
        Arguments: speedup - speedup interval in minutes
        """
        self._speedup = timedelta(minutes=minutes, hours=hours, days=days)
            
    def scheduler_loop(self, interval=60):
        now = datetime.now()
        while not self.stopped():
            event_schedules = EventSchedule.objects.filter(active=True)
            for schedule in event_schedules:
                try:
                    if schedule.should_fire(now):
                        # call the callback function
                        # possibly passing in args and kwargs
                        module, callback = schedule.callback.rsplit(".", 1)
                        module = __import__(module, globals(), locals(), [callback])
                        callback = getattr(module, callback)
                        if schedule.callback_args and schedule.callback_kwargs:
                            callback(self._router, *schedule.callback_args, **schedule.callback_kwargs)
                        elif schedule.callback_args:
                            callback(self._router, *schedule.callback_args)
                        elif schedule.callback_kwargs:
                            callback(self._router, **schedule.callback_kwargs)
                        else:
                            callback(self._router)
                        if schedule.count:
                            schedule.count = schedule.count - 1
                            # should we delete expired schedules? we do now.
                            if schedule.count <= 0: 
                                schedule.deactivate()
                            else: schedule.save()
                        # should we delete expired schedules? we do now.
                        if schedule.end_time:
                            if now > schedule.end_time:
                                schedule.deactivate()
                except Exception, e:
                    # Don't prevent exceptions from killing the thread
                    self._router.error("Problem in scheduler for: %s. %s" % (schedule,
                                                                             e.message))
                    
            if self._speedup is not None: # debugging/testing only!
                now = now + self._speedup
                time.sleep(1)
            else: 
                next_run = now + timedelta(seconds=interval)
                updated_now = datetime.now()
                while updated_now < next_run:
                    # we add another second since system time runs at microsecond accuracy
                    # whereas python time is only second accuracy
                    time.sleep((next_run - updated_now + timedelta(seconds=1)).seconds)
                    updated_now = datetime.now()
                now = next_run
