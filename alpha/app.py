#!/usr/bin/env python
# vim: noet

import rapidsms

# a pointless app to demonstrate the structure
# of sms applications without magic decorators
class App(rapidsms.app.Base):
	def incoming(msg):
		msg.respond("Alpha!")
