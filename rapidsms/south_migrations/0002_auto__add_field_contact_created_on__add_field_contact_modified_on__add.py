# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models
from django.utils.timezone import now


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Contact.created_on'
        db.add_column(u'rapidsms_contact', 'created_on',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, default=now(), blank=True),
                      keep_default=False)

        # Adding field 'Contact.modified_on'
        db.add_column(u'rapidsms_contact', 'modified_on',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now=True, default=now(), blank=True),
                      keep_default=False)

        # Adding field 'Connection.created_on'
        db.add_column(u'rapidsms_connection', 'created_on',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, default=now(), blank=True),
                      keep_default=False)

        # Adding field 'Connection.modified_on'
        db.add_column(u'rapidsms_connection', 'modified_on',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now=True, default=now(), blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Contact.created_on'
        db.delete_column(u'rapidsms_contact', 'created_on')

        # Deleting field 'Contact.modified_on'
        db.delete_column(u'rapidsms_contact', 'modified_on')

        # Deleting field 'Connection.created_on'
        db.delete_column(u'rapidsms_connection', 'created_on')

        # Deleting field 'Connection.modified_on'
        db.delete_column(u'rapidsms_connection', 'modified_on')


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
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identity': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'rapidsms.contact': {
            'Meta': {'object_name': 'Contact'},
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '6', 'blank': 'True'}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        }
    }

    complete_apps = ['rapidsms']