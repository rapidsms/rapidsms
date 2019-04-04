# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DeliveryReport',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('date_sent', models.DateTimeField()),
                ('message_id', models.CharField(max_length=255, verbose_name='Message ID')),
                ('identity', models.CharField(max_length=100)),
                ('sms_id', models.CharField(max_length=36, verbose_name='SMS ID')),
                ('smsc', models.CharField(max_length=255, verbose_name='SMSC')),
                ('status', models.SmallIntegerField(choices=[(1, 'Delivery Success'), (2, 'Delivery Failure'), (4, 'Message Buffered'), (8, 'SMSC Submit'), (16, 'SMSC Reject')])),
                ('status_text', models.CharField(max_length=255)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
