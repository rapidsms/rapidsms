#!/usr/bin/env python
# vim: noet

import rapidsms

if __name__ == "__main__":
	
	# a pointless app to demonstrate the structure
	# of sms applications without magic decorators
	class AlphaApp(rapidsms.app.Base):
		def incoming(msg):
			msg.respond("Alpha!")
	
	# another pointless app
	class BetaApp(rapidsms.app.Base):
		def incoming(msg):
			msg.respond("Beta!")
	
	router = rapidsms.router.Router()
	
	# register all apps with rapidsms, to
	# start receiving incoming messages
	router.register_app(AlphaApp())
	router.register_app(BetaApp())
	
	# wait for incoming sms
	router.serve_forever()
