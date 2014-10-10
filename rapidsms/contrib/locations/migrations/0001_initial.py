# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('parent_id', models.PositiveIntegerField(null=True, blank=True)),
                ('parent_type', models.ForeignKey(blank=True, to='contenttypes.ContentType', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LocationType',
            fields=[
                ('name', models.CharField(max_length=100)),
                ('slug', models.SlugField(unique=True, serialize=False, primary_key=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Point',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('latitude', models.DecimalField(max_digits=13, decimal_places=10)),
                ('longitude', models.DecimalField(max_digits=13, decimal_places=10)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='location',
            name='point',
            field=models.ForeignKey(blank=True, to='locations.Point', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='location',
            name='type',
            field=models.ForeignKey(related_name=b'locations', blank=True, to='locations.LocationType', null=True),
            preserve_default=True,
        ),
    ]
