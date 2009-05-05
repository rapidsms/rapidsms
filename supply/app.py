#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


import rapidsms
from formslogic import *

class App(rapidsms.app.App):

    def __init__(self, router, calling_app=None):
        super(App, self).__init__(router)
        
    def start(self):
        pass

    def parse(self, message):
        pass

    def handle(self, message):
        pass 


    def outgoing(self, message):
        pass 

    def add_form_handler_to(self, app):
        '''Tell the supply app to register with another app.  This is confusing,
           but by setting it up this way, no one else is dependant on SupplyFormsLogic()'''
        app.add_form_handler("supply", SupplyFormsLogic())
