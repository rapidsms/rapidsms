#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import rapidsms

class App (rapidsms.app.App):
    def ajax_GET_recipients(self, params):
        return {
            "columns": ("Name", "Height"),
            
            "recipients": [
                ("asm", "Adam Mckaig",  "180cm"),
                ("emw", "Evan Wheeler", "190cm"),
                ("cz",  "Cory Zue",     "185cm")
            ]
        }
