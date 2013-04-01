# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'BackendMessage'
        db.create_table(u'database_backendmessage', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('direction', self.gf('django.db.models.fields.CharField')(max_length=1, db_index=True)),
            ('message_id', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('external_id', self.gf('django.db.models.fields.CharField')(max_length=64, blank=True)),
            ('identity', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('text', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'database', ['BackendMessage'])


    def backwards(self, orm):
        # Deleting model 'BackendMessage'
        db.delete_table(u'database_backendmessage')


    models = {
        u'database.backendmessage': {
            'Meta': {'object_name': 'BackendMessage'},
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'direction': ('django.db.models.fields.CharField', [], {'max_length': '1', 'db_index': 'True'}),
            'external_id': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identity': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'message_id': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'text': ('django.db.models.fields.TextField', [], {})
        }
    }

    complete_apps = ['database']