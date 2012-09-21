Deploying Robust Applications
=================================

The main thing is: stop using runserver and switch over to Apache or your real server of choice.

For all deployments:

* errors: -> send out an email/sms (logtracker app - no sms integration here). http://github.com/tostan/rapidsms-tostan/tree/master/apps/logtracker/
* route startup on system boot -> route init
* route dies -> log + restart system (rapidsms-route.cron - checks pid file and process list. restarts process if dead. depends on 2, above)
* website availability from the external world -> uptime
* change your db config to be utf8-friendly. if using mysql, use InnoDB.
* make sure your server has an accurate time and date

When running on a physical machine:

* power out -> send out an email/sms (matt's childcount solution. monitors ups signals and sends out sms via a presumably-working route). in the childcount repo somewhere, i don't use this.
* remote access -> reverse ssh (matt's solution for childcount. the folks who did inveneo's amat - which is how i sneak in the backend when tostan's public url breaks, which it does a lot - agree that reverse ssh should work fine now. it wasn't around when amat was born.) i don't currently use this, am using the old amat from inveneo.

When running on a physical machine with a hardware modem:

* route hangs -> log + restart system (this is what i wrote. checks http responsiveness + sends an email. no other backend support, no outgoing sms yet. depends on this backend.)

Miscellaneously good
=======================

* install ntp to keep system clock up to date::

    apt-get install ntp
    /etc/init.d ntp stop
    ntpdate -u pool.ntp.org
    /etc/init.d ntp start
