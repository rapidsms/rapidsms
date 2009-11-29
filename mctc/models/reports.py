from django.db import models
from django.db.models import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from mctc.models.general import Case, Provider
from mctc.models.logs import MessageLog

from datetime import datetime, date, timedelta
import md5

class Report:
    def get_alert_recipients(self):
        """ Each report will send an alert, how it will choose when to send an alert
        is up to the model, however. """
        # this is the reporter, the provider or the CHW depending what you call it
        provider = self.provider
        facility = provider.clinic
        assert facility, "This provider does not have a clinic."

        recipients = []

        # find all the people assigned to alerts from this facility
        for user in facility.following_clinics.all():
            # only send if they want
            if user.alerts:
                if user not in recipients:
                    recipients.append(user)
        
        
        # find all the users monitoring this user
        for user in provider.following_users.all():
            if user.alerts:
                if user not in recipients:
                    recipients.append(user)

        return recipients

class Observation(models.Model):
    uid = models.CharField(max_length=15)
    name = models.CharField(max_length=255)
    letter = models.CharField(max_length=2, unique=True)

    class Meta:
        app_label = "mctc"
        ordering = ("name",)

    def __unicode__(self):
        return self.name

class DiarrheaObservation(models.Model):
    uid = models.CharField(max_length=15, primary_key=True)
    name = models.CharField(max_length=255)
    letter = models.CharField(max_length=2, unique=True)

    class Meta:
        app_label = "mctc"
        ordering = ("name",)

    def __unicode__(self):
        return self.name
        
class ReportMalaria(Report, models.Model):
    class Meta:
        get_latest_by = 'entered_at'
        ordering = ("-entered_at",)
        app_label = "mctc"
        verbose_name = "Malaria Report"
        verbose_name_plural = "Malaria Reports"
    
    case = models.ForeignKey(Case, db_index=True)
    provider = models.ForeignKey(Provider, db_index=True)
    entered_at = models.DateTimeField(db_index=True)
    bednet = models.BooleanField(db_index=True)
    result = models.BooleanField(db_index=True) 
    observed = models.ManyToManyField(Observation, blank=True)       

    def get_dictionary(self):
        return {
            'result': self.result,
            'result_text': self.result and "Y" or "N",
            'bednet': self.bednet,
            'bednet_text': self.bednet and "Y" or "N",
            'observed': ", ".join([k.name for k in self.observed.all()]),            
        }
        
    def zone(self):
        return self.case.zone.name
        
    def results_for_malaria_bednet(self):
    	bednet = "N"
    	if self.bednet is True:
    	   bednet = "Y"	
    	return "%s"%(bednet)

    def results_for_malaria_result(self):
    	result = "-"
    	if self.bednet is True:
    	   result = "+"	
    	return "%s"%(result)

    def name(self):
        return "%s %s" % (self.case.first_name, self.case.last_name)
    
    def provider_number(self):
        return self.provider.mobile
        
    def save(self, *args):
        if not self.id:
            self.entered_at = datetime.now()
        super(ReportMalaria, self).save(*args)
        
    @classmethod
    def count_by_provider(cls,provider, duration_end=None,duration_start=None):
        if provider is None:
            return None
        try:
            if duration_start is None or duration_end is None:
                return cls.objects.filter(provider=provider).count()
            return cls.objects.filter(entered_at__lte=duration_end, entered_at__gte=duration_start).filter(provider=provider).count()
        except models.ObjectDoesNotExist:
            return None
        
class ReportMalnutrition(Report, models.Model):
    
    MODERATE_STATUS         = 1
    SEVERE_STATUS           = 2
    SEVERE_COMP_STATUS      = 3
    HEALTHY_STATUS = 4
    STATUS_CHOICES = (
        (MODERATE_STATUS,       _('MAM')),
        (SEVERE_STATUS,         _('SAM')),
        (SEVERE_COMP_STATUS,    _('SAM+')),
        (HEALTHY_STATUS, _("Healthy")),
    )

    case        = models.ForeignKey(Case, db_index=True)
    provider    = models.ForeignKey(Provider, db_index=True)
    entered_at  = models.DateTimeField(db_index=True)
    muac        = models.IntegerField(_("MUAC (mm)"), null=True, blank=True)
    height      = models.IntegerField(_("Height (cm)"), null=True, blank=True)
    weight      = models.FloatField(_("Weight (kg)"), null=True, blank=True)
    observed    = models.ManyToManyField(Observation, blank=True)
    status      = models.IntegerField(choices=STATUS_CHOICES, db_index=True, blank=True, null=True)
    
    class Meta:
        app_label = "mctc"
        verbose_name = "Malnutrition Report"
        verbose_name_plural = "Malnutrition Reports"
        get_latest_by = 'entered_at'
        ordering = ("-entered_at",)

    def get_dictionary(self):
        return {
            'muac'      : "%d mm" % self.muac,
            'observed'  : ", ".join([k.name for k in self.observed.all()]),
            'diagnosis' : self.get_status_display(),
            'diagnosis_msg' : self.diagnosis_msg(),
        }
                               
                        
    def __unicode__ (self):
        return "#%d" % self.id
        
    def symptoms(self):
      	return ", ".join([k.name for k in self.observed.all()])
    
    def zone(self):
        return self.case.zone.name
        
    def name(self):
        return "%s %s" % (self.case.first_name, self.case.last_name) 
        
    def provider_number(self):
        return self.provider.mobile
            
    def diagnose (self):
        complications = [c for c in self.observed.all() if c.uid != "edema"]
        edema = "edema" in [ c.uid for c in self.observed.all() ]
        self.status = ReportMalnutrition.HEALTHY_STATUS
        if edema or self.muac < 110:
            if complications:
                self.status = ReportMalnutrition.SEVERE_COMP_STATUS
            else:
                self.status = ReportMalnutrition.SEVERE_STATUS
        elif self.muac < 125:
            self.status =  ReportMalnutrition.MODERATE_STATUS

    def diagnosis_msg(self):
        if self.status == ReportMalnutrition.MODERATE_STATUS:
            msg = "MAM Child requires supplemental feeding."
        elif self.status == ReportMalnutrition.SEVERE_STATUS:
            msg = "SAM Patient requires OTP care"
        elif self.status == ReportMalnutrition.SEVERE_COMP_STATUS:
            msg = "SAM+ Patient requires IMMEDIATE inpatient care"
        else:
            msg = "Child is not malnourished"
   
        return msg

    def save(self, *args):
        if not self.id:
            self.entered_at = datetime.now()
        super(ReportMalnutrition, self).save(*args)
       
    @classmethod
    def count_by_provider(cls,provider, duration_end=None,duration_start=None):
        if provider is None:
            return None
        try:
            if duration_start is None or duration_end is None:
                return cls.objects.filter(provider=provider).count()
            return cls.objects.filter(entered_at__lte=duration_end, entered_at__gte=duration_start).filter(provider=provider).count()
        except models.ObjectDoesNotExist:
            return None 

class Lab(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=10)
    
    def __unicode__(self):
        return self.name

    class Meta:
        app_label = "mctc"
        ordering = ("code",)        

class LabDiagnosis(models.Model):
    lab = models.ForeignKey(Lab)
    diagnosis = models.ForeignKey("ReportDiagnosis")
    amount = models.IntegerField(blank=True, null=True)
    result = models.BooleanField(blank=True)

    def __unicode__(self):
        return "%s, %s - %s" % (self.lab, self.diagnosis, self.amount)

    class Meta:
        app_label = "mctc"

class DiagnosisCategory(models.Model):
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name

    class Meta:
        app_label = "mctc"
        ordering = ("name",)
        
class Diagnosis(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=10)
    category = models.ForeignKey(DiagnosisCategory)
    mvp_code = models.CharField(max_length=255)
    instructions = models.TextField(blank=True)
    
    def __unicode__(self):
        return self.mvp_code

    class Meta:
        app_label = "mctc"
        ordering = ("code",)
        verbose_name = "Diagnosis Code"
        verbose_name_plural = "Diagnosis Codes"
        
class ReportDiagnosis(Report, models.Model):
    case = models.ForeignKey(Case, db_index=True)
    provider = models.ForeignKey(Provider, db_index=True)
    diagnosis = models.ManyToManyField(Diagnosis)
    lab = models.ManyToManyField(Lab, through=LabDiagnosis)
    text = models.TextField()
    entered_at  = models.DateTimeField(db_index=True)
    
    def __unicode__(self):
        return self.case

    class Meta:
        verbose_name = "Diagnosis Report"
        app_label = "mctc"

    def save(self, *args):
        if not self.id:
            self.entered_at = datetime.now()
        super(ReportDiagnosis, self).save(*args)

    def get_dictionary(self):
        extra = []
        for ld in LabDiagnosis.objects.filter(diagnosis=self):
            if ld.amount:
                extra.append("%s %s" % (ld.lab.code, ld.amount))
            else:
                extra.append("%s%s" % (ld.lab.code, ld.result and "+" or "-"))
                
        return {
            "diagnosis": ", ".join([str(d) for d in self.diagnosis.all()]),
            "labs": ", ".join([str(d) for d in self.lab.all()]),
            "labs_text": ", ".join(extra)
        }

class ReportDiarrhea(Report, models.Model):
    
    MODERATE_STATUS         = 1
    DANGER_STATUS           = 2
    SEVERE_STATUS           = 3
    HEALTHY_STATUS          = 4
    STATUS_CHOICES = (
        (MODERATE_STATUS,   _('Moderate')),
        (DANGER_STATUS,     _('Danger')),
        (SEVERE_STATUS,     _('Severe')),
        (HEALTHY_STATUS,    _("Healthy")),
    )

    case        = models.ForeignKey(Case, db_index=True)
    provider    = models.ForeignKey(Provider, db_index=True)
    entered_at  = models.DateTimeField(db_index=True)
    ors         = models.BooleanField()
    days        = models.IntegerField(_("Number of days"))    
    observed    = models.ManyToManyField(DiarrheaObservation, blank=True)
    status      = models.IntegerField(choices=STATUS_CHOICES, db_index=True, blank=True, null=True)
    
    class Meta:
        app_label = "mctc"
        verbose_name = "Diarrhea Report"
        verbose_name_plural = "Diarrhea Reports"
        get_latest_by = 'entered_at'
        ordering = ("-entered_at",)

    def get_dictionary(self):
        return {
            'ors'       : "ORS: %s" % ("yes" if self.ors else "no"),
            'days'      : "Days: %d" % self.days,
            'observed'  : ", ".join([k.name for k in self.observed.all()]),
            'diagnosis' : self.get_status_display(),
            'diagnosis_msg' : self.diagnosis_msg(),
        }
                               
    def __unicode__ (self):
        return "#%d" % self.id

    def diagnose (self):
        if self.days >= 3 or self.observed.all().count() > 0:
            self.status = ReportDiarrhea.DANGER_STATUS
        else:
            self.status = ReportDiarrhea.MODERATE_STATUS

    def diagnosis_msg(self):
        if self.status == ReportDiarrhea.MODERATE_STATUS:
            msg = "MOD Patient should take ORS."
        elif self.status == ReportDiarrhea.SEVERE_STATUS:
            msg = "SEV Patient must be referred at clinic."
        elif self.status == ReportDiarrhea.DANGER_STATUS:
            msg = "DANG Patient must go to Clinic."
        else:
            msg = "HEAL Patient not in danger."
   
        return msg

    def save(self, *args):
        if not self.id:
            self.entered_at = datetime.now()
        super(ReportDiarrhea, self).save(*args)
        
class ReportCHWStatus(Report, models.Model):
    class Meta:
        verbose_name = "CHW Perfomance Report"
        app_label = "mctc"
    @classmethod
    def get_providers_by_clinic(cls, duration_start, duration_end, muac_duration_start, clinic_id=None):
        
    
        ps      = []
        fields  = []
        counter = 0
        clinic_cases = 0
        clinic_mrdt = 0
        clinic_muac = 0
        clinic_sent = 0
        clinic_processed = 0
        clinic_refused = 0
        
        if clinic_id is not None:
            providers = Provider.list_by_clinic(clinic_id)
            for provider in providers:
                p = {}
                counter = counter + 1
                p['counter'] = "%d"%counter
                p['provider'] = provider
                p['num_cases'] = Case.count_by_provider(provider)
                p_muac = ReportMalaria.count_by_provider(provider, duration_end, duration_start)
                p['num_malaria_reports'] = p_muac
                clinic_mrdt = clinic_mrdt + p_muac 
                num_cases = Case.count_by_provider(provider)
                clinic_cases = clinic_cases + num_cases
                num_muac = ReportMalnutrition.count_by_provider(provider, duration_end, muac_duration_start)
                clinic_muac = clinic_muac + num_muac
                if num_cases == 0:
                    muac_percentage = 0
                else:
                    muac_percentage  = round(float(float(num_muac)/float(num_cases))*100, 0)
                p['num_muac_reports'] = "%d %% (%s/%s)"%(muac_percentage, num_muac, num_cases)
                sms_sent = MessageLog.count_by_provider(provider, duration_end, duration_start)
                clinic_sent = clinic_sent + sms_sent
                p['sms_sent'] = sms_sent
                sms_processed = MessageLog.count_processed_by_provider(provider, duration_end, duration_start)
                clinic_processed = clinic_processed + sms_processed
                p['sms_processed'] = sms_processed
                sms_refused = MessageLog.count_refused_by_provider(provider, duration_end, duration_start)
                clinic_refused = clinic_refused + sms_refused
                p['sms_refused'] = sms_refused
                if p['sms_sent'] != 0:
                    p['sms_rate'] = int(float(float(p['sms_processed'])/float(p['sms_sent'])*100))
                else:
                    p['sms_rate'] = 0
                #p['sms_rate'] = "%s%%"%p['sms_rate']
                last_activity = MessageLog.days_since_last_activity(provider)
                if last_activity == "":
                    p['days_since_last_activity'] = "No Activity"
                else:
                    p['days_since_last_activity'] = "%s days ago"%last_activity
                                    
                ps.append(p)
            
            #ps = sorted(ps)
            # Summary    
            p = {}
            p['counter'] = ""
            p['provider'] = "Summary"
            p['num_cases'] = clinic_cases
            p['num_malaria_reports'] = clinic_mrdt
            num_cases = clinic_cases
            num_muac = clinic_muac
            if num_cases == 0:
                muac_percentage = 0
            else:
                muac_percentage  = round(float(float(num_muac)/float(num_cases))*100, 0)
            p['num_muac_reports'] = "%d %% (%s/%s)"%(muac_percentage, num_muac, num_cases)
            p['sms_sent'] = clinic_sent
            p['sms_processed'] = clinic_processed
            p['sms_refused'] = clinic_refused
            if p['sms_sent'] != 0:
                p['sms_rate'] = int(float(float(p['sms_processed'])/float(p['sms_sent'])*100))
            else:
                p['sms_rate'] = 0
            #p['sms_rate'] = "%s%%"%p['sms_rate']
            p['days_since_last_activity'] = "" 
                                
            ps.append(p)
                    # caseid +|Y lastname firstname | sex | dob/age | guardian | provider  | date
            fields.append({"name": '#', "column": None, "bit": "{{ object.counter }}" })
            fields.append({"name": 'PROVIDER', "column": None, "bit": "{{ object.provider }}" })
            fields.append({"name": 'NUMBER OF CASES', "column": None, "bit": "{{ object.num_cases}}" })
            fields.append({"name": 'MRDT', "column": None, "bit": "{{ object.num_malaria_reports }}" })
            fields.append({"name": 'MUAC', "column": None, "bit": "{{ object.num_muac_reports }}" })
            fields.append({"name": 'RATE', "column": None, "bit": "{{ object.sms_rate }}% ({{ object.sms_processed }}/{{ object.sms_sent }})" })
            fields.append({"name": 'LAST ACTVITY', "column": None, "bit": "{{ object.days_since_last_activity }}" })
            return ps, fields        
        
class ReportAllPatients(Report, models.Model):
    class Meta:
        verbose_name = "CHW Perfomance Report"
        app_label = "mctc"
    @classmethod
    def by_provider(cls, provider_id=None):    
        qs      = []
        fields  = []
        counter = 0
        if provider_id is not None:
            cases   = Case.objects.order_by("last_name").filter(provider=provider_id)
            
            for case in cases:
                q   = {}
                q['case']   = case
                counter = counter + 1
                q['counter'] = "%d"%counter
                try:
                    muacc   = ReportMalnutrition.objects.filter(case=case).latest()
                    #q['malnut'] = u"%(diag)s on %(date)s" % {'diag': muacc.diagnosis_msg(), 'date': muacc.entered_at.strftime("%Y-%m-%d")}
                    q['malnut_muac'] = "%s (%smm)"%(muacc.get_status_display(), muacc.muac)
                    q['malnut_symptoms'] = muacc.symptoms()
                except ObjectDoesNotExist:
                    q['malnut_muac'] = ""
                    q['malnut_symptoms'] = ""
        
                try:
                    orsc   = ReportDiarrhea.objects.filter(case=case).latest()
                    q['diarrhea'] = u"%(diag)s on %(date)s" % {'diag': orsc.diagnosis_msg(), 'date': orsc.entered_at.strftime("%Y-%m-%d")}
                except ObjectDoesNotExist:
                    q['diarrhea'] = None
                    
                try:
                    mrdtc   = ReportMalaria.objects.filter(case=case).latest()
                    mrdtcd  = mrdtc.get_dictionary()
                    #q['malaria'] = u"result:%(res)s bednet:%(bed)s obs:%(obs)s on %(date)s" % {'res': mrdtcd['result_text'], 'bed': mrdtcd['bednet_text'], 'obs': mrdtcd['observed'], 'date': mrdtc.entered_at.strftime("%Y-%m-%d")}
                    q['malaria_result'] = mrdtc.results_for_malaria_result()
                    q['malaria_bednet'] = mrdtc.results_for_malaria_bednet()
                except ObjectDoesNotExist:
                    q['malaria_result'] = ""
                    q['malaria_bednet'] = ""
                    
                try:
                    dc      = ReportDiagnosis.objects.filter(case=case).latest('entered_at')
                    dcd     = dc.get_dictionary()
                    q['diagnosis'] = u"diag:%(diag)s labs:%(lab)s on %(date)s" % {'diag': dcd['diagnosis'], 'lab': dcd['labs_text'], 'date': dc.entered_at.strftime("%Y-%m-%d")}
                except ObjectDoesNotExist:
                    q['diagnosis'] = None
                
                qs.append(q)
            # caseid +|Y lastname firstname | sex | dob/age | guardian | provider  | date
            fields.append({"name": '#', "column": None, "bit": "{{ object.counter }}" })
            fields.append({"name": 'PID#', "column": None, "bit": "{{ object.case.ref_id }}" })
            fields.append({"name": 'NAME', "column": None, "bit": "{{ object.case.last_name }} {{ object.case.first_name }}" })
            fields.append({"name": 'SEX', "column": None, "bit": "{{ object.case.gender }}" })
            fields.append({"name": 'AGE', "column": None, "bit": "{{ object.case.age }}" })
            fields.append({"name": 'REGISTERED', "column": None, "bit": "{{ object.case.date_registered }}" })
            fields.append({"name": 'MRDT', "column": None, "bit": "{{ object.malaria_result }}" })
            fields.append({"name": 'BEDNET', "column": None, "bit": "{{ object.malaria_bednet }}" })
            fields.append({"name": 'CMAM', "column": None, "bit": "{{ object.malnut_muac }}" })
            fields.append({"name": 'SYMPTOMS', "column": None, "bit": "{{ object.malnut_symptoms}}" })
            return qs, fields
