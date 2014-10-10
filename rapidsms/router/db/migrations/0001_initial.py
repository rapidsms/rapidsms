# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rapidsms', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.CharField(default=b'Q', max_length=1, db_index=True, choices=[(b'Q', b'Queued'), (b'R', b'Received'), (b'P', b'Processing'), (b'S', b'Sent'), (b'D', b'Delivered'), (b'E', b'Errored')])),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(db_index=True, auto_now=True, null=True)),
                ('sent', models.DateTimeField(null=True, blank=True)),
                ('delivered', models.DateTimeField(null=True, blank=True)),
                ('direction', models.CharField(db_index=True, max_length=1, choices=[(b'I', b'Incoming'), (b'O', b'Outgoing')])),
                ('text', models.TextField()),
                ('external_id', models.CharField(max_length=1024, blank=True)),
                ('in_response_to', models.ForeignKey(related_name=b'responses', blank=True, to='db.Message', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Transmission',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.CharField(db_index=True, max_length=1, choices=[(b'Q', b'Queued'), (b'R', b'Received'), (b'P', b'Processing'), (b'S', b'Sent'), (b'D', b'Delivered'), (b'E', b'Errored')])),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(db_index=True, auto_now=True, null=True)),
                ('sent', models.DateTimeField(null=True, blank=True)),
                ('delivered', models.DateTimeField(null=True, blank=True)),
                ('connection', models.ForeignKey(related_name=b'transmissions', to='rapidsms.Connection')),
                ('message', models.ForeignKey(related_name=b'transmissions', to='db.Message')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
