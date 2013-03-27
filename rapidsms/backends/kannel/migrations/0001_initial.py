# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'DeliveryReport'
        db.create_table(u'kannel_deliveryreport', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('date_sent', self.gf('django.db.models.fields.DateTimeField')()),
            ('message_id', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('identity', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('sms_id', self.gf('django.db.models.fields.CharField')(max_length=36)),
            ('smsc', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('status', self.gf('django.db.models.fields.SmallIntegerField')()),
            ('status_text', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal(u'kannel', ['DeliveryReport'])


    def backwards(self, orm):
        # Deleting model 'DeliveryReport'
        db.delete_table(u'kannel_deliveryreport')


    models = {
        u'kannel.deliveryreport': {
            'Meta': {'object_name': 'DeliveryReport'},
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_sent': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identity': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'message_id': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'sms_id': ('django.db.models.fields.CharField', [], {'max_length': '36'}),
            'smsc': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'status': ('django.db.models.fields.SmallIntegerField', [], {}),
            'status_text': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['kannel']