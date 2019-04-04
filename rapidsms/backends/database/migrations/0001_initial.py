# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BackendMessage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('direction', models.CharField(db_index=True, max_length=1, choices=[('I', 'Incoming'), ('O', 'Outgoing')])),
                ('message_id', models.CharField(max_length=64)),
                ('external_id', models.CharField(max_length=64, blank=True)),
                ('identity', models.CharField(max_length=100)),
                ('text', models.TextField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
