# vim: ai ts=4 sts=4 et sw=4
import rapidsms
from time import time
from reporters.models import PersistantConnection
from airtime.models import AirtimePins
from time import localtime, strftime, time
from datetime import datetime

class App (rapidsms.app.App):
    def start (self):
        # specifies the frequency (in seconds) to send airtime credits to responders
        self._frequency =  3 * 24 * 3600 # 3 days in seconds

    def parse (self, message):
        """Parse and annotate messages in the parse phase."""
        pass

    def handle (self, message):
        """Add your main application logic in the handle phase."""
        pass

    def cleanup (self, message):
        """Perform any clean up after all handlers have run in the
           cleanup phase."""
        pass

    def outgoing (self, message):
        # I'm going to assume that I've gotten the reporter's connection
        con = PersistantConnection.from_message(message)
        
        # determine if the user is due for a recharge
        time_period = time() - self._frequency
        try:
            last_airtime = AirtimePins.objects.filter(time_used__gt=strftime('%Y-%m-%d %H:%M:%S', localtime(time_period)), connection=con).latest('time_used')
        except (AirtimePins.DoesNotExist):
            try:
                # The user is due hence let's obtain a recharge pin
                airtime = AirtimePins.vend_airtime(con.identity)
                airtime.used = True
                airtime.time_used = datetime.now()
                airtime.connection = con
                airtime.save()

                msg_text = "Thanks for using RapidSMS. Please load this credit: %s" % airtime.pin
                msg = message.connection.backend.message(con.identity, msg_text)
                msg.send()

            except (AirtimePins.DoesNotExist):
                # There probably should be a more elegant way of handling this
                self.error("No airtime pins available!")
                pass

    def stop (self):
        """Perform global app cleanup when the application is stopped."""
        pass
