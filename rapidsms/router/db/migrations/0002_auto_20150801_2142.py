# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('db', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='direction',
            field=models.CharField(max_length=1, db_index=True, choices=[('I', 'Incoming'), ('O', 'Outgoing')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='message',
            name='status',
            field=models.CharField(max_length=1, db_index=True, choices=[('Q', 'Queued'), ('R', 'Received'), ('P', 'Processing'), ('S', 'Sent'), ('D', 'Delivered'), ('E', 'Errored')], default='Q'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='transmission',
            name='status',
            field=models.CharField(max_length=1, db_index=True, choices=[('Q', 'Queued'), ('R', 'Received'), ('P', 'Processing'), ('S', 'Sent'), ('D', 'Delivered'), ('E', 'Errored')]),
            preserve_default=True,
        ),
    ]
