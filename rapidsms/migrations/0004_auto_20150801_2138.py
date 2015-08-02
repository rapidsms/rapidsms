# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rapidsms', '0003_delete_backendmessage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contact',
            name='language',
            field=models.CharField(help_text='The language which this contact prefers to communicate in, as a W3C language tag. If this field is left blank, RapidSMS will default to the value in LANGUAGE_CODE.', max_length=6, blank=True),
            preserve_default=True,
        ),
    ]
