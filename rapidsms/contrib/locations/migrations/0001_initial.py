# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Point'
        db.create_table(u'locations_point', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('latitude', self.gf('django.db.models.fields.DecimalField')(max_digits=13, decimal_places=10)),
            ('longitude', self.gf('django.db.models.fields.DecimalField')(max_digits=13, decimal_places=10)),
        ))
        db.send_create_signal(u'locations', ['Point'])

        # Adding model 'LocationType'
        db.create_table(u'locations_locationtype', (
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=50, primary_key=True)),
        ))
        db.send_create_signal(u'locations', ['LocationType'])

        # Adding model 'Location'
        db.create_table(u'locations_location', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('point', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['locations.Point'], null=True, blank=True)),
            ('type', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='locations', null=True, to=orm['locations.LocationType'])),
            ('parent_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'], null=True, blank=True)),
            ('parent_id', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'locations', ['Location'])


    def backwards(self, orm):
        # Deleting model 'Point'
        db.delete_table(u'locations_point')

        # Deleting model 'LocationType'
        db.delete_table(u'locations_locationtype')

        # Deleting model 'Location'
        db.delete_table(u'locations_location')


    models = {
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'locations.location': {
            'Meta': {'object_name': 'Location'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parent_id': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'parent_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']", 'null': 'True', 'blank': 'True'}),
            'point': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['locations.Point']", 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'locations'", 'null': 'True', 'to': u"orm['locations.LocationType']"})
        },
        u'locations.locationtype': {
            'Meta': {'object_name': 'LocationType'},
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50', 'primary_key': 'True'})
        },
        u'locations.point': {
            'Meta': {'object_name': 'Point'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.DecimalField', [], {'max_digits': '13', 'decimal_places': '10'}),
            'longitude': ('django.db.models.fields.DecimalField', [], {'max_digits': '13', 'decimal_places': '10'})
        }
    }

    complete_apps = ['locations']