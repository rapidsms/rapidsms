#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import rapidsms

class App (rapidsms.app.App):
    def ajax_GET_recipients(self, params):
        
        def __app_dict(app):
            """Fetches the recipient list from a given app, and
               combines with meta-data, to avoid requiring app
               authors to include their own every time."""
            
            has_search = hasattr(app, "ajax_GET_recipient_search")
            
            info = {
                "search": has_search,
                "title": app.title,
                "slug":  app.slug }
            
            # the method can overwrite the meta-data, if it wants
            info.update(app.ajax_GET_recipients(params))
            
            return info
        
        return [
            __app_dict(app)
            for app in self.router.apps
            
            # only include apps that will provide
            # recipients, to avoid empty sections
            if hasattr(app, "ajax_GET_recipients")\
               and (app != self)]
