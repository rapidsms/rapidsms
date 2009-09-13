#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from models import *
from rapidsms.message import StatusCodes
from reporters.models import *
from form.formslogic import FormsLogic
import re

class NigeriaFormsLogic(FormsLogic):
    ''' This class will hold the nigeria-specific forms logic.
        I'm not sure whether this will be the right structure
        this was just for getting something hooked up '''
    
    # this is a simple structure we use to describe the forms.  
    # maps token names to db names
    _form_lookups = {
                     "nets" : {
                               "class" : NetDistribution,
                               "display" : "nets",
                               "fields" : (
                                           ("location", "location"), 
                                           ("distributed", "distributed"), 
                                           ("expected", "expected"), 
                                           ("actual", "actual"),
                                           ("discrepancy", "discrepancy")
                                           )
                               },
                     "netcards" : {"class" : CardDistribution, 
                              "display" : "net cards",
                              "fields" : (
                                          ("location", "location"), 
                                          ("settlements", "settlements"), 
                                          ("people", "people"), 
                                          ("issued", "distributed"),
                                          )
                              }
                     }
        
    _foreign_key_lookups = {"Location" : "code" }

    def validate(self, *args, **kwargs):
        message = args[0]
        form_entry = args[1]
        # in case we need help, build a valid reminder string
        # TODO put this in the db!
        required = ["location", "role", "firstname"]
        help = ("%s register " % form_entry.domain.code.abbreviation.lower()) +\
                " ".join(["<%s>" % t for t in required])
        if form_entry.form.code.abbreviation == "register":
            data = form_entry.to_dict()

            # check that ALL FIELDS were provided
            missing = [t for t in required if data[t] is None]
            
            # missing fields! collate them, and
            # send back a friendly non-localized
            # error message, then abort
            if missing:
                mis_str = ", ".join(missing)
                return ["Missing fields: %s" % mis_str, help]
            
            # parse the name via Reporter
            flat_name = data.pop("firstname") + " " + data.pop("secondname") + " " + data.pop("thirdname")
            data["alias"], data["first_name"], data["last_name"] =\
                Reporter.parse_name(flat_name.strip())
            
            # all fields were present and correct, so copy them into the
            # form_entry, for "actions" to pick up again without re-fetching
            form_entry.rep_data = data
            
            # parse the roles out. 
            # TODO: how can this be done generically
            role_code = data.pop("role")
            role = None
            try:
                role = Role.objects.get(code__iexact=role_code)
            except Role.DoesNotExist:
                # try to match the pattern
                for db_role in Role.objects.all():
                    if db_role.match(role_code):
                        role = db_role
                        break
            if not role:
                return ["Unknown role code: %s" % role_code]
            data["role"] = role
            
            
            # nothing went wrong. the data structure
            # is ready to spawn a Reporter object
            return None
        elif form_entry.form.code.abbreviation in self._form_lookups.keys():
            # we know all the fields in this form are required, so make sure they're set
            # TODO check the token's required flag
            required_tokens = [form_token.token for form_token in form_entry.form.form_tokens.all() if form_token.required]
            for tokenentry in form_entry.tokenentry_set.all():
                if tokenentry.token in required_tokens:
                    # found it, as long as the data isn't empty remove it
                    if tokenentry.data:
                        required_tokens.remove(tokenentry.token)
            if required_tokens:
                req_token_names = [token.abbreviation for token in required_tokens]
                errors = "The following fields are required: " + ", ".join(req_token_names)
                return [errors]
            return None
        
    

    def actions(self, *args, **kwargs):
        message = args[0]
        form_entry = args[1]
        if form_entry.form.code.abbreviation== "register":

            data = form_entry.rep_data
            # load the location and role objects via their codes
            data["location"] = Location.objects.get(code__iexact=data["location"])
            # this happens in validation now
            # data["role"]     = Role.objects.get(code__iexact=data["role"])
            
            # spawn and save the reporter using the
            # data we collected in self.validate
            rep = Reporter(**data)
            conn = PersistantConnection.from_message(message)
            # check for duplicate registration.
            if Reporter.exists(rep, conn):
                # if they already exist just re-send a confirmation but don't
                # create a new instance. 
                message.respond("Hello again %s!  You are already registered as a %s at %s %s."\
                                % (rep.first_name, rep.role, rep.location, rep.location.type), StatusCodes.OK)
                return
            # if they didn't exist then save them
            rep.save()

            # we can assume that the new reporter will be using
            # this device again, so register a connection. this
            # automatically logs them in, so they can start
            # reporting straight away
            conn.reporter = rep
            conn.save()

            # notify the user that everyting went okay
            # TODO: proper (localized?) messages here
            message.respond("Hello %s! You are now registered as %s at %s %s."\
                % (rep.first_name, rep.role, rep.location, rep.location.type), StatusCodes.OK)

        elif self._form_lookups.has_key(form_entry.form.code.abbreviation):
            to_use = self._form_lookups[form_entry.form.code.abbreviation]
            form_class = to_use["class"]
            field_list = to_use["fields"]
            # create and save the model from the form data
            instance = self._model_from_form(message, form_entry, form_class, dict(field_list), self._foreign_key_lookups)
            instance.time = message.date
            
            # if the reporter isn't set then populate the connection object.
            # this means that at least one (actually exactly one) is set
            # the method above sets this property in the instance
            # if it was found.
            if not hasattr(instance, "reporter") or not instance.reporter:
                instance.connection = message.persistant_connection
                response = ""
            # personalize response if we have a registered reporter
            else:
                response = "Thank you %s. " % (instance.reporter.first_name)
            instance.save()
            response = response + "Received report for %s %s: " % (form_entry.domain.code.abbreviation.upper(), to_use["display"].upper())
            # this line pulls any attributes that are present into 2-item lists
            attrs = [[attr[1], str(getattr(instance, attr[1]))] for attr in field_list if hasattr(instance, attr[1])]
            # joins the inner list on "=" and the outer on ", " so we get 
            # attr1=value1, attr2=value2
            response = response + ", ".join(["=".join(t) for t in attrs])
            if not instance.reporter:
                response = response + ". Please register your phone"
            message.respond(response, StatusCodes.OK)
