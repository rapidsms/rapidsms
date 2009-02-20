#!/usr/bin/env python
# vim: noet

class Client:
	def __init__(self, host="localhost", port="8100"):
		self.host = host
		self.port = port
	
	def __repr__(self):
		return '<rapidsms.spomsky.Client host="%s", port="%s">' % (self.host, self.port)
