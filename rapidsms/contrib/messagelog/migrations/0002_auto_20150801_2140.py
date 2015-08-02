# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('messagelog', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='direction',
            field=models.CharField(max_length=1, choices=[('I', 'Incoming'), ('O', 'Outgoing')]),
            preserve_default=True,
        ),
    ]
