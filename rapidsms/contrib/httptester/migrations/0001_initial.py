# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'HttpTesterMessage'
        db.create_table(u'httptester_httptestermessage', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('direction', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('identity', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('text', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'httptester', ['HttpTesterMessage'])


    def backwards(self, orm):
        # Deleting model 'HttpTesterMessage'
        db.delete_table(u'httptester_httptestermessage')


    models = {
        u'httptester.httptestermessage': {
            'Meta': {'ordering': "['date', 'id']", 'object_name': 'HttpTesterMessage'},
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'direction': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identity': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'text': ('django.db.models.fields.TextField', [], {})
        }
    }

    complete_apps = ['httptester']