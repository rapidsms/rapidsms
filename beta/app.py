#!/usr/bin/env python
# vim: noet

import rapidsms

# another pointless app
class App(rapidsms.app.Base):
	def incoming(msg):
		msg.respond("Beta!")
