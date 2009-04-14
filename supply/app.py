#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


import rapidsms
from formslogic import *

class App(rapidsms.app.App):

    def __init__(self, title, router, calling_app=None):
        super(App, self).__init__(title, router)
        self.calling_app = calling_app 
        if calling_app:
            calling_app.form_app.register("supply", SupplyFormsLogic())

    def start(self):
        pass

    def parse(self, message):
        pass

    def handle(self, message):
        pass 


    def outgoing(self, message):
        pass 

