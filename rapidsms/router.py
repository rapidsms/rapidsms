#!/usr/bin/env python
# vim: noet

import spomsky
import time

class Router:
	def __init__(self):
		self.backends = []
		self.apps = []
	
	def register_app(self, app):
		self.apps.append(app)
	
	def add_backend(self, *args):
		self.backends.append(
			spomsky.Client(*args))
	
	def serve_forever(self):
		
		# if no backends have been set up, add one with
		# no arguments, for local dev and debugging
		if len(self.backends) == 0:
			self.add_backend()
		
		# dump some debug info for now
		print "BACKENDS: %r" % (self.backends)
		print "APPS: %r" % (self.apps)
		print "SERVING FOREVER..."
		
		# block forever! TODO: replace this
		# with a thread for each backend
		while(True):
			time.sleep(1)
