from django.db import models
from django.utils.translation import ugettext

def _(txt): return txt

from django.contrib.auth.models import User, Group

import rapidsms
from rapidsms.parsers.keyworder import Keyworder
from rapidsms.message import Message
from rapidsms.connection import Connection

from models.logs import MessageLog, log, elog

from models.general import Provider, User
from models.general import Facility, Case, CaseNote, Zone

from models.reports import ReportMalnutrition, ReportMalaria, Observation, DiarrheaObservation, ReportDiarrhea
from models.reports import ReportDiagnosis, Diagnosis, Lab, LabDiagnosis

import re, time, datetime

find_diagnostic_re = re.compile('( -[\d\.]+)' ,re.I)
find_lab_re =  re.compile('(/[A-Z]+)([\+-])(\d*:?)', re.I)

def authenticated (func):
    def wrapper (self, message, *args):
        if message.sender:
            return func(self, message, *args)
        else:
            message.respond(_("%s is not a registered number.")
                            % message.peer)
            return True
    return wrapper

class HandlerFailed (Exception):
    pass

class App (rapidsms.app.App):
    MAX_MSG_LEN = 140
    keyword = Keyworder()

    def start (self):
        """Configure your app in the start phase."""
        pass

    def parse (self, message):
        provider = Provider.by_mobile(message.peer)
        if provider:
            message.sender = provider.user
        else:
            message.sender = None
        message.was_handled = False

    def cleanup (self, message):
        log = MessageLog(mobile=message.peer,
                         sent_by=message.sender,
                         text=message.text,
                         was_handled=message.was_handled)
        log.save()

    def handle (self, message):
        try:
            func, captures = self.keyword.match(self, message.text)
        except TypeError:
            # didn't find a matching function
            # make sure we tell them that we got a problem
            #message.respond(_("Unknown or incorrectly formed command: %(msg)s... Please re-check your message") % {"msg":message.text[:10]})
            self.int2dom(message, _("Unknown or incorrectly formed command: %(msg)s... Please re-check your message") % {"msg":message.text[:10]})
            return False
        try:
            handled = func(self, message, *captures)
        except HandlerFailed, e:
            #message.respond(e.message)
            self.int2dom(message,e.message)
            handled = True
        except Exception, e:
            # TODO: log this exception
            # FIXME: also, put the contact number in the config
            #message.respond(_("An error occurred. Please call 0733202270."))
            self.int2dom(message, _("An error occurred. Please call 0733202270."))
            elog(message.sender, message.text)
            raise
        message.was_handled = bool(handled)
        return handled

    @keyword("join (\S+) (\S+) (\S+)(?: ([a-z]\w+))?")
    def join (self, message, code, last_name, first_name, username=None):
        try:
            clinic = Facility.objects.get(codename__iexact=code)
        except Facility.DoesNotExist:
            raise HandlerFailed(_("The given password is not recognized."))

        if username is None:
            # FIXME: this is going to run into charset issues
            username = (first_name[0] + last_name).lower()
        else:
            # lower case usernames ... also see FIXME above?
            username = username.lower()
        if User.objects.filter(username__iexact=username).count():
            raise HandlerFailed(_(
                "Username '%s' is already in use. " +
                "Reply with: JOIN <last> <first> <username>") % username)

        # todo: use the more generic get_description if possible
        info = {
            "username"   : username,
            "user_first_name" : first_name.title(),
            "user_last_name"  : last_name.title()
        }
        user = User(username=username, first_name=first_name.title(), last_name=last_name.title())
        user.save()

        mobile = message.peer
        in_use = Provider.by_mobile(mobile)
        provider = Provider(mobile=mobile, user=user,
                            clinic=clinic, active=not bool(in_use))
        provider.save()

        if in_use:
            info.update({
                "user_last_name"  : in_use.user.last_name.upper(),
                "user_first_name" : in_use.user.first_name,
                "other"      : in_use.user.username,
                "mobile"     : mobile,
                "clinic"     : provider.clinic.name,
            })
            #message.respond(_(
            #    "Phone %(mobile)s is already registered to %(user_last_name)s, " +
            #   "%(user_first_name)s. Reply with 'CONFIRM %(username)s'.") % info)
            self.int2dom(message, _(
                "Phone %(mobile)s is already registered to %(user_last_name)s, " +
                "%(user_first_name)s. Reply with 'CONFIRM %(username)s'.") % info)
        else:
            info.update({
                "id"        : provider.id,
                "mobile"    : mobile,
                "clinic"    : provider.clinic.name,
                "user_last_name" : last_name.upper()
            })
            self.respond_to_join(message, info)
        log(provider, "provider_registered")            
        return True

    def respond_to_join(self, message, info):
        #message.respond(
        #   _("%(mobile)s registered to @%(username)s " +
        #      "(%(user_last_name)s, %(user_first_name)s) at %(clinic)s.") % info)
        self.int2dom(message, 
            _("%(mobile)s registered to @%(username)s " +
              "(%(user_last_name)s, %(user_first_name)s) at %(clinic)s.") % info)

    @keyword(r'confirm (\w+)')
    def confirm_join (self, message, username):
        mobile   = message.peer
        try:
            user = User.objects.get(username__iexact=username)
        except User.DoesNotExist:
            self.respond_not_registered(username)
        for provider in Provider.objects.filter(mobile=mobile):
            if provider.user.id == user.id:
                provider.active = True
            else:
                provider.active = False
            provider.save()
        info = provider.get_dictionary()
        self.respond_to_join(message, info)
        log(provider, "confirmed_join")
        return True
    
    @keyword(r'check system')
    #@authenticated
    def check_system_status (self, message):
        mobile   = message.peer
        #message.respond(_("Hello %s, system is up.")% mobile)
        self.int2dom(message, _("Hello %s, system is up.")% mobile)
        return True
    
    def respond_not_registered (self, message, target):
        raise HandlerFailed(_("User @%s is not registered.") % target)

    def find_provider (self, target):
        try:
            if re.match(r'^\d+$', target):
                provider = Provider.objects.get(id=target)
            else:
                user = User.objects.get(username__iexact=target)
                provider = Provider.objects.get(user=user)
            return provider
        except models.ObjectDoesNotExist:
            # FIXME: try looking up a group
            self.respond_not_registered(message, target)

    @keyword(r'\@(\w+) (.+)')
    @authenticated
    def direct_message (self, message, target, text):
        provider = self.find_provider(target)
        try:
            mobile = provider.mobile
        except:
            self.respond_not_registered(message, target)
        sender = message.sender.username
        #return message.forward(mobile, "@%s> %s" % (sender, text))
        return self.int2dom(message, "@%s> %s" % (sender, text),mobile)

    # Register a new patient
    @keyword(r'new (\S+) (\S+) ([MF]) ([\d\-]+)( \D+)?( \d+)?( z\d+)?')
    @authenticated
    def new_case (self, message, last, first, gender, dob,
                  guardian="", contact="", zone=None):
        provider = message.sender.provider
        if not zone:
            if provider.clinic:
                zone = provider.clinic.zone
        else:
            zone = Zone.objects.get(number=zone[1:])

        dob = re.sub(r'\D', '', dob)
        try:
            dob = time.strptime(dob, "%d%m%y")
        except ValueError:
            try:
                dob = time.strptime(dob, "%d%m%Y")
            except ValueError:
                raise HandlerFailed(_("Couldn't understand date: %s") % dob)
        dob = datetime.date(*dob[:3])
        if guardian:
            guardian = guardian.title()
        # todo: move this to a more generic get_description
        info = {
            "first_name" : first.title(),
            "last_name"  : last.title(),
            "gender"     : gender.upper()[0],
            "dob"        : dob,
            "guardian"   : guardian,
            "mobile"     : contact,
            "provider"   : provider,
            "zone"       : zone
        }

        ## check to see if the case already exists
        iscase = Case.objects.filter(first_name=info['first_name'], last_name=info['last_name'], provider=info['provider'], dob=info['dob'])
        if iscase:
            #message.respond(_(
            #"%(last_name)s, %(first_name)s has already been registered by you.") % info)
            info["PID"] = iscase[0].id
            self.info(iscase[0].id)
            self.info(info)
            self.int2dom(message, _(
            "%(last_name)s, %(first_name)s (+%(PID)s) has already been registered by %(provider)s.") % info)
            # TODO: log this message
            return True
        case = Case(**info)
        case.save()

        info.update({
            "id": case.ref_id,
            "last_name": last.upper(),
            "age": case.age()
        })
        if zone:
            info["zone"] = zone.name
        #message.respond(_(
        #    "New +%(id)s: %(last_name)s, %(first_name)s %(gender)s/%(age)s " +
        #    "(%(guardian)s) %(zone)s") % info)
        
        self.int2dom(message, _(
            "New +%(id)s: %(last_name)s, %(first_name)s %(gender)s/%(age)s " +
            "(%(guardian)s) %(zone)s") % info)
        log(case, "patient_created")
        return True

    def find_case (self, ref_id):
        try:
            return Case.objects.get(ref_id=int(ref_id))
        except Case.DoesNotExist:
            raise HandlerFailed(_("Case +%s not found.") % ref_id)

    @keyword(r'cancel \+?(\d+)')
    @authenticated
    def cancel_case (self, message, ref_id):
        case = self.find_case(ref_id)
        if case.reportmalnutrition_set.count():
            raise HandlerFailed(_(
                "Cannot cancel +%s: case has malnutrition reports.") % ref_id)
                
        if case.reportmalaria_set.count():
            raise HandlerFailed(_(
                "Cannot cancel +%s: case has malaria reports.") % ref_id)
                
        if case.reportdiagnosis_set.count():
            raise HandlerFailed(_(
                "Cannot cancel +%s: case has diagnosis reports.") % ref_id)

        case.delete()
        #message.respond(_("Case +%s cancelled.") % ref_id)
        self.int2dom(message, _("Case +%s cancelled.") % ref_id)
        
        log(message.sender.provider, "case_cancelled")        
        return True

    @keyword(r'transfer \+?(\d+) (?:to )?\@?(\w+)')
    @authenticated
    def transfer_case (self, message, ref_id, target):
        provider = message.sender.provider
        case = self.find_case(ref_id)
        new_provider = self.find_provider(target) 
        case.provider = new_provider
        case.save()
        info = new_provider.get_dictionary()
        info["ref_id"] = case.ref_id
        #message.respond(_("Case +%(ref_id)s transferred to @%(username)s " +
         #                 "(%(user_last_name)s, %(user_last_name)s).") % info)
        self.int2dom(message, _("Case +%(ref_id)s transferred to @%(username)s " +
                          "(%(user_last_name)s, %(user_last_name)s).") % info)
        #message.forward(_("Case +%s transferred to you from @%s.") % (
         #                 case.ref_id, provider.user.username))
        self.int2dom(message, _("Case +%s transferred to you from @%s.") % (
                          case.ref_id, provider.user.username))
        log(case, "case_transferred")        
        return True
 
    @keyword(r'list(?: \+)?')
    @authenticated
    def list_cases (self, message):
        # FIXME: should only return active cases here
        # needs order by to cope with what unit tests expect
        cases = Case.objects.filter(provider=message.sender.provider).order_by("ref_id")
        text  = ""
        for case in cases:
            item = "+%s %s %s. %s/%s" % (case.ref_id, case.last_name.upper(),
                case.first_name[0].upper(), case.gender, case.age())
            if len(text) + len(item) + 2 >= self.MAX_MSG_LEN:
                #message.respond(text)
                self.int2dom(message, text)
                text = ""
            if text: text += ", "
            text += item
        if text:
            #message.respond(text)
            self.int2dom(message, text)
        return True

    @keyword(r'list\s@')
    @authenticated
    def list_providers (self, message):
        providers = Provider.objects.all()
        text  = ""
        for provider in providers:
            item = "@%s %s" % (provider.id, provider.user.username)
            if len(text) + len(item) + 2 >= self.MAX_MSG_LEN:
                #message.respond(text)
                self.int2dom(message, text)
                text = ""
            if text: text += ", "
            text += item
        if text:
            #message.respond(text)
            self.int2dom(message, text)
        return True

    @keyword(r's(?:how)? \+?(\d+)')
    @authenticated
    def show_case (self, message, ref_id):
        case = self.find_case(ref_id)
        info = case.get_description()

        if case.guardian: info["guardian"] = "(%s) " % case.guardian
        if case.zone: info["zone"] = case.zone.name
        """ message.respond(_(
            "+%(id)s %(status)s %(last_name)s, %(first_name)s "
            "%(gender)s/%(age)s %(guardian)s%(zone)s") % info)
        """
        self.int2dom(message, _(
            "+%(id)s %(status)s %(last_name)s, %(first_name)s "
            "%(gender)s/%(age)s %(guardian)s%(zone)s") % info)
        return True

    #CMAM Reports

    @keyword(r'muac \+(\d+) ([\d\.]+)( [\d\.]+)?( [\d\.]+)?( (?:[a-z]\s*)+)')
    @authenticated
    def report_case (self, message, ref_id, muac,
                     weight, height, complications):
        case = self.find_case(ref_id)
        try:
            muac = float(muac)
            if muac < 30: # muac is in cm?
                muac *= 10
            muac = int(muac)
        except ValueError:
            raise HandlerFailed(
                _("Can't understand MUAC (mm): %s") % muac)

        if weight is not None:
            try:
                weight = float(weight)
                if weight > 100: # weight is in g?
                    weight /= 1000.0
            except ValueError:
                raise HandlerFailed("Can't understand weight (kg): %s" % weight)

        if height is not None:
            try:
                height = float(height)
                if height < 3: # weight height in m?
                    height *= 100
                height = int(height)
            except ValueError:
                raise HandlerFailed("Can't understand height (cm): %s" % height)

        observed, choices = self.get_observations(complications)
        self.delete_similar(case.reportmalnutrition_set)

        provider = message.sender.provider
        report = ReportMalnutrition(case=case, provider=provider, muac=muac,
                        weight=weight, height=height)
        report.save()
        for obs in observed:
            report.observed.add(obs)
        report.diagnose()
        report.save()

        choice_term = dict(choices)

        info = case.get_dictionary()
        info.update(report.get_dictionary())

        msg = _("%(diagnosis_msg)s. +%(ref_id)s %(last_name)s, %(first_name_short)s, %(gender)s/%(months)s (%(guardian)s). MUAC %(muac)s") % info

        if weight: msg += ", %.1f kg" % weight
        if height: msg += ", %.1d cm" % height
        if observed: msg += ", " + info["observed"]

        #message.respond("MUAC> " + msg)
        self.int2dom(message, "MUAC> " + msg)

        if report.status in (report.MODERATE_STATUS,
                           report.SEVERE_STATUS,
                           report.SEVERE_COMP_STATUS):
            alert = _("@%(username)s reports %(msg)s") % {"username":provider.user.username, "msg":msg}
            recipients = [provider]
            for query in (Provider.objects.filter(alerts=True),
                          Provider.objects.filter(clinic=provider.clinic)):
                for recipient in query:
                    if recipient in recipients: continue
                    recipients.append(recipient)
                    #message.forward(recipient.mobile, alert)
        log(case, "muac_taken")
        return True

    @keyword(r'n(?:ote)? \+(\d+) (.+)')
    @authenticated
    def note_case (self, message, ref_id, note):
        case = self.find_case(ref_id)
        CaseNote(case=case, created_by=message.sender, text=note).save()
        #message.respond(_("Note added to case +%s.") % ref_id)
        self.int2dom(message, _("Note added to case +%s.") % ref_id)
        log(case, "note_added")        
        return True

    @keyword(r'd \+(\d+ )(.*)')
    @authenticated
    def diagnosis(self, message, ref_id, text):
        case = self.find_case(ref_id)
        provider = message.sender.provider
        diags = []
        labs = []

        hits = find_diagnostic_re.findall(message.text)
        for hit in hits:
            code = hit[2:]
            try:
                diags.append(Diagnosis.objects.get(code__iexact=code))
            except Diagnosis.DoesNotExist:
                raise HandlerFailed("Unknown diagnosis code: %s" % code)

        hits = find_lab_re.findall(text)
        for hit in hits:
            code, sign, number = hit
            try:
                # the code starts with /
                labs.append([Lab.objects.get(code__iexact=code[1:]), sign, number])
            except Lab.DoesNotExist:
                raise HandlerFailed("Unknown lab code: %s" % code)

        self.delete_similar(case.reportdiagnosis_set)
        report = ReportDiagnosis(case=case, provider=provider, text=message.text)
        report.save()
        for diag in diags:
            report.diagnosis.add(diag)
        for lab, sign, number in labs:
            ld = LabDiagnosis()
            ld.lab = lab
            ld.result = int(sign == "+")
            if number:
                ld.amount = number
            ld.diagnosis = report
            ld.save()
        report.save()

        info = case.get_dictionary()
        info.update(report.get_dictionary())
        if info["labs_text"]:
            info["labs_text"] = "%sLabs: %s" % (info["diagnosis"] and " " or "", info["labs_text"])

        #message.respond(_("D> +%(ref_id)s %(first_name_short)s.%(last_name)s %(diagnosis)s%(labs_text)s") % info)
        self.int2dom(message, _("D> +%(ref_id)s %(first_name_short)s.%(last_name)s %(diagnosis)s%(labs_text)s") % info)
        # add in the forward of instructions to the case provider
        # if that it is not the reporter of the issue        

        
        instructions = []       
        for diagnosis in report.diagnosis.all():
            if diagnosis.instructions:
                instructions.append(diagnosis.instructions)

        if instructions:
            if provider != case.provider:
                # there's a different provider
                info = {"ref_id":ref_id, "instructions":(", ".join(instructions))}
                #message.forward(case.provider.mobile, "D> +%(ref_id)s %(instructions)s" % info)
                self.int2dom(message, "D> +%(ref_id)s %(instructions)s" % info,case.provider.mobile)
                
        log(case, "diagnosis_taken")        
        return True        

    @keyword(r'mrdt \+(\d+) ([yn]) ([yn])?(.*)')
    @authenticated
    def report_malaria(self, message, ref_id, result, bednet, observed):
        case = self.find_case(ref_id)
        observed, choices = self.get_observations(observed)
        self.delete_similar(case.reportmalaria_set)
        provider = message.sender.provider

        result = result.lower() == "y"
        bednet = bednet.lower() == "y"

        report = ReportMalaria(case=case, provider=provider, result=result, bednet=bednet)
        report.save()
        for obs in observed:
            report.observed.add(obs)
        report.save()

        # build up an information dictionary
        info = case.get_dictionary()
        info.update(report.get_dictionary())
        info.update(provider.get_dictionary())

        # this could all really do with cleaning up
        # note that there is always an alert that goes out
        if not result:
            if observed: info["observed"] = ", (%s)" % info["observed"]
            msg = _("MRDT> Child +%(ref_id)s, %(last_name)s, %(first_name)s, "\
                    "%(gender)s/%(months)s (%(guardian)s), %(village)s. RDT=%(result_text)s,"\
                    " Bednet=%(bednet_text)s%(observed)s. Please refer patient IMMEDIATELY "\
                    "for clinical evaluation" % info)
            # alerts to health team
            alert = _("MRDT> Negative MRDT with Fever. +%(ref_id)s, %(last_name)s,"\
                      " %(first_name)s, %(gender)s/%(months)s %(village)s. Patient "\
                      "requires IMMEDIATE referral. Reported by CHW %(provider_name)s "\
                      "@%(provider_user)s m:%(provider_mobile)s." % info)

        else:
            # this is all for if child has tested postive
            # and is really just abut
            years, months = case.years_months()
            tabs, yage = None, None
            # just reformatted to make it look like less ugh
            if years < 1:
                if months < 2: tabs, yage = None, None
                else: tabs, yage = 1, "less than 3"
            elif years < 3: tabs, yage = 1, "less than 3"
            elif years < 9: tabs, yage = 2, years
            elif years < 15: tabs, yage = 3, years
            else: tabs, yage = 4, years

            # messages change depending upon age and dangers
            dangers = report.observed.filter(uid__in=("vomiting", "appetite", "breathing", "confusion", "fits"))
            # no tabs means too young
            if not tabs:
                info["instructions"] = "Child is too young for treatment. Please refer IMMEDIATELY to clinic"
            else:
                # old enough to take tabs, but lets format msg
                if dangers:
                    info["danger"] = " and danger signs (" + ",".join([ u.name for u in dangers ]) + ")"                        
                    info["instructions"] = "Refer to clinic immediately after %s "\
                                           "tab%s of Coartem is given" % (tabs, (tabs > 1) and "s" or "")
                else:
                    info["danger"] = ""
                    info["instructions"] = "Child is %s. Please provide %s tab%s "\
                                           "of Coartem (ACT) twice a day for 3 days" % (yage, tabs, 
                                           (tabs > 1) and "s" or "")

            # finally build out the messages
            msg = _("MRDT> Child +%(ref_id)s, %(last_name)s, %(first_name)s, "\
                    "%(gender)s/%(months)s has MALARIA%(danger)s. %(instructions)s" % info)

            alert = _("MRDT> Child +%(ref_id)s, %(last_name)s, %(first_name)s, "\
                      "%(gender)s/%(months)s (%(village)s) has MALARIA%(danger)s. "\
                      "CHW: @%(provider_user)s %(provider_mobile)s" % info)

        #message.respond(msg)
        self.int2dom(message, msg)
        recipients = report.get_alert_recipients()
        for recipient in recipients:
            #message.forward(recipient.mobile, alert)
            self.int2dom(message, alert,recipient.mobile)

        log(case, "mrdt_taken")        
        return True

# DIARRHEA
    # follow up on diarrhea
    @keyword(r'ors \+(\d+) ([yn])')
    @authenticated
    def followup_diarrhea(self, message, ref_id, is_ok):
        case    = self.find_case(ref_id)
        is_ok   = True if is_ok == "y" else False

        provider = message.sender.provider
        report = ReportDiarrhea.objects.get(case=case)
        
        if is_ok:
            report.status   = ReportDiarrhea.HEALTHY_STATUS
            report.save()
        else:
            report.status   = ReportDiarrhea.SEVERE_STATUS
            report.save()

            info = report.case.get_dictionary()
            info.update(report.get_dictionary())
   
            msg = _("%(diagnosis_msg)s. +%(ref_id)s %(last_name)s, %(first_name_short)s, %(gender)s/%(months)s (%(guardian)s). %(days)s, %(ors)s") % info
            if report.observed.all().count() > 0: msg += ", " + info["observed"]
            
            #message.respond("DIARRHEA> " + msg)
            self.int2dom(message, "DIARRHEA> " + msg)

        if report.status in (report.MODERATE_STATUS,
                           report.SEVERE_STATUS,
                           report.DANGER_STATUS):
            alert = _("@%(username)s reports %(msg)s") % {"username":provider.user.username, "msg":msg}
            recipients = [provider]
            for query in (Provider.objects.filter(alerts=True),
                          Provider.objects.filter(clinic=provider.clinic)):
                for recipient in query:
                    if recipient in recipients: continue
                    recipients.append(recipient)
                    #message.forward(recipient.mobile, alert)
                    self.int2dom(message, alert, recipient.mobile)
        log(case, "diarrhea_fu_taken")
        return True

    @keyword(r'ors \+(\d+) ([yn]) (\d+)\s?([a-z\s]*)')
    @authenticated
    def report_diarrhea(self, message, ref_id, ors, days, complications):
        case = self.find_case(ref_id)

        ors     = True if ors == "y" else False
        days    = int(days)

        observed, choices = self.get_diarrheaobservations(complications)
        self.delete_similar(case.reportdiarrhea_set)

        provider = message.sender.provider
        report = ReportDiarrhea(case=case, provider=provider, ors=ors, days=days)
        report.save()
        for obs in observed:
            report.observed.add(obs)
        report.diagnose()
        report.save()

        choice_term = dict(choices)

        info = case.get_dictionary()
        info.update(report.get_dictionary())

        msg = _("%(diagnosis_msg)s. +%(ref_id)s %(last_name)s, %(first_name_short)s, %(gender)s/%(months)s (%(guardian)s). %(days)s, %(ors)s") % info

        if observed: msg += ", " + info["observed"]

        #message.respond("DIARRHEA> " + msg)
        self.int2dom(message, "DIARRHEA> " + msg)

        if report.status in (report.MODERATE_STATUS,
                           report.SEVERE_STATUS,
                           report.DANGER_STATUS):
            alert = _("@%(username)s reports %(msg)s") % {"username":provider.user.username, "msg":msg}
            recipients = [provider]
            for query in (Provider.objects.filter(alerts=True),
                          Provider.objects.filter(clinic=provider.clinic)):
                for recipient in query:
                    if recipient in recipients: continue
                    recipients.append(recipient)
                    #message.forward(recipient.mobile, alert)
                    self.int2dom(message, alert,recipient.mobile)
        log(case, "diarrhea_taken")
        return True

    def delete_similar(self, queryset):
        try:
            last_report = queryset.latest("entered_at")
            if (datetime.datetime.now() - last_report.entered_at).days == 0:
                # last report was today. so delete it before filing another.
                last_report.delete()
        except models.ObjectDoesNotExist:
            pass

    def get_observations(self, text):
        choices  = dict( [ (o.letter, o) for o in Observation.objects.all() ] )
        observed = []
        if text:
            text = re.sub(r'\W+', ' ', text).lower()
            for observation in text.split(' '):
                obj = choices.get(observation, None)
                if not obj:
                    if observation != 'n':
                        raise HandlerFailed("Unknown observation code: %s" % observation)
                else:
                    observed.append(obj)
        return observed, choices

    def get_diarrheaobservations(self, text):
        choices  = dict( [ (o.letter, o) for o in DiarrheaObservation.objects.all() ] )
        observed = []
        if text:
            text = re.sub(r'\W+', ' ', text).lower()
            for observation in text.split(' '):
                obj = choices.get(observation, None)
                if not obj:
                    if observation != 'n':
                        raise HandlerFailed("Unknown observation code: %s" % observation)
                else:
                    observed.append(obj)
        return observed, choices

    def int2dom(self, message, text, mobile=None):
        if mobile is None:
            mobile = message.peer
        mobile = mobile.replace("+254","0")
        message.forward(mobile, text)