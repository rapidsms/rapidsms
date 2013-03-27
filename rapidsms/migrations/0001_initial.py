# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Backend'
        db.create_table(u'rapidsms_backend', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=20)),
        ))
        db.send_create_signal(u'rapidsms', ['Backend'])

        # Adding model 'App'
        db.create_table(u'rapidsms_app', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('module', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'rapidsms', ['App'])

        # Adding model 'Contact'
        db.create_table(u'rapidsms_contact', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('language', self.gf('django.db.models.fields.CharField')(max_length=6, blank=True)),
        ))
        db.send_create_signal(u'rapidsms', ['Contact'])

        # Adding model 'Connection'
        db.create_table(u'rapidsms_connection', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('backend', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rapidsms.Backend'])),
            ('identity', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('contact', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rapidsms.Contact'], null=True, blank=True)),
        ))
        db.send_create_signal(u'rapidsms', ['Connection'])

        # Adding unique constraint on 'Connection', fields ['backend', 'identity']
        db.create_unique(u'rapidsms_connection', ['backend_id', 'identity'])


    def backwards(self, orm):
        # Removing unique constraint on 'Connection', fields ['backend', 'identity']
        db.delete_unique(u'rapidsms_connection', ['backend_id', 'identity'])

        # Deleting model 'Backend'
        db.delete_table(u'rapidsms_backend')

        # Deleting model 'App'
        db.delete_table(u'rapidsms_app')

        # Deleting model 'Contact'
        db.delete_table(u'rapidsms_contact')

        # Deleting model 'Connection'
        db.delete_table(u'rapidsms_connection')


    models = {
        u'rapidsms.app': {
            'Meta': {'object_name': 'App'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'module': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
        },
        u'rapidsms.backend': {
            'Meta': {'object_name': 'Backend'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '20'})
        },
        u'rapidsms.connection': {
            'Meta': {'unique_together': "(('backend', 'identity'),)", 'object_name': 'Connection'},
            'backend': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['rapidsms.Backend']"}),
            'contact': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['rapidsms.Contact']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identity': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'rapidsms.contact': {
            'Meta': {'object_name': 'Contact'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '6', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        }
    }

    complete_apps = ['rapidsms']