# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def move_backend_messages_to_database_app(apps, schema_editor):
    rapidsms_BackendMessage = apps.get_model('rapidsms', 'BackendMessage')
    database_BackendMessage = apps.get_model('database', 'BackendMessage')

    for m in rapidsms_BackendMessage.objects.all():
        database_BackendMessage.objects.create(
            name=m.name,
            date=m.date,
            direction=m.direction,
            message_id=m.message_id,
            external_id=m.external_id,
            identity=m.identity,
            text=m.text,
        )


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0001_initial'),
        ('rapidsms', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(move_backend_messages_to_database_app),
    ]
