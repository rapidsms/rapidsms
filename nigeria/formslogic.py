#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from models import *
from apps.reporters.models import *
from apps.form.formslogic import FormsLogic

class NigeriaFormsLogic(FormsLogic):
    ''' This class will hold the nigeria-specific forms logic.
        I'm not sure whether this will be the right structure
        this was just for getting something hooked up '''
    
    _form_lookups = {
                     "nets" : {
                               "class" : NetDistribution,
                               "display" : "nets",
                               "fields" : {
                                           "netloc" : "location", 
                                           "distributed" : "distributed", 
                                           "expected" : "expected", 
                                           "actual" : "actual",
                                           "discrepancy" : "discrepancy", 
                                           }
                               },
                     "net" : {"class" : CardDistribution, 
                              "display" : "net cards",
                              "fields" : {
                                          "cardloc" : "location", 
                                          "villages" : "settlements", 
                                          "people" : "people", 
                                          "coupons" : "distributed",
                                          }
                              }
                     }
        
    _foreign_key_lookups = {"Location" : "code" }

    def validate(self, *args, **kwargs):
        message = args[0]
        form_entry = args[1]
        if form_entry.form.type == "register":
            data = form_entry.to_dict()
            print "\n\n%r\n\n" % data
                
            # check that ALL FIELDS were provided
            required = ["location", "role", "password", "name"]
            missing = [t for t in required if data[t] is None]
            
            # in case we need help, build a valid reminder string
            help = ("%s register " % form_entry.domain.code.lower()) +\
                " ".join(["<%s>" % t for t in required])
                
            # missing fields! collate them, and
            # send back a friendly non-localized
            # error message, then abort
            if missing:
                mis_str = ", ".join(missing)
                return ["Missing fields: %s" % mis_str, help]
            
            try:
                # attempt to load the location and role objects
                # via their codes, which will raise if nothing
                # was found TODO: combine the exceptions
                data["location"] = Location.objects.get(code__iexact=data["location"])
                data["role"]     = Role.objects.get(code__iexact=data["role"])
            
            except Location.DoesNotExist:
                return ["Invalid location code: %s" %
                    data["location"], help]
            
            except Role.DoesNotExist:
                return ["Invalid role code: %s" %
                    data["role"], help]
            
            # parse the name via Reporter
            data["alias"], data["first_name"], data["last_name"] =\
                Reporter.parse_name(data.pop("name"))
            
            # check that the name/alias
            # hasn't already been registered
            reps = Reporter.objects.filter(alias=data["alias"])
            if len(reps):
                return ["Already been registed: %s" %
                    data["alias"], help]
            
            # all fields were present and correct, so copy them into the
            # form_entry, for "actions" to pick up again without re-fetching
            form_entry.rep_data = data
            
            # nothing went wrong. the data structure
            # is ready to spawn a Reporter object
            return None
        elif form_entry.form.type in self._form_lookups.keys() and (not hasattr(message,"reporter") or not message.reporter):  
            
            return [ "You must register your phone before submitting data" ]
        
    

    def actions(self, *args, **kwargs):
        message = args[0]
        form_entry = args[1]
        if form_entry.form.type == "register":

            # spawn and save the reporter using the
            # data we collected in self.validate
            rep = Reporter.objects.create(**form_entry.rep_data)

            # we can assume that the new reporter will be using
            # this device again, so register a connection. this
            # automatically logs them in, so they can start
            # reporting straight away
            conn = PersistantConnection.from_message(message)
            conn.reporter = rep
            conn.save()

            # notify the user that everyting went okay
            # TODO: proper (localized?) messages here
            message.respond("Reporter %s (#%d/%d) added" % (rep.alias, rep.pk, conn.pk))

        elif self._form_lookups.has_key(form_entry.form.type):
            to_use = self._form_lookups[form_entry.form.type]
            form_class = to_use["class"]
            field_map = to_use["fields"]
            instance = self._model_from_form(message, form_entry, form_class, field_map, self._foreign_key_lookups)
            instance.save()
            response = "Received report for %s %s: " % (form_entry.domain.code, to_use["display"])
            fields = [] 
            for token, model_attr in field_map.items():
                if hasattr(instance, model_attr):
                    fields.append(model_attr + "=" + str(getattr(instance, model_attr)))
            message.respond(response + ", ".join(fields))
                    
