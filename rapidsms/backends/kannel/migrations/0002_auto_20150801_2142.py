# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('kannel', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deliveryreport',
            name='message_id',
            field=models.CharField(max_length=255, verbose_name='Message ID'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='deliveryreport',
            name='sms_id',
            field=models.CharField(max_length=36, verbose_name='SMS ID'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='deliveryreport',
            name='smsc',
            field=models.CharField(max_length=255, verbose_name='SMSC'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='deliveryreport',
            name='status',
            field=models.SmallIntegerField(choices=[(1, 'Delivery Success'), (2, 'Delivery Failure'), (4, 'Message Buffered'), (8, 'SMSC Submit'), (16, 'SMSC Reject')]),
            preserve_default=True,
        ),
    ]
