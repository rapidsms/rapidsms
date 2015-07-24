# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rapidsms', '0002_alter_contact_language'),
    ]

    operations = [
        migrations.DeleteModel(
            name='BackendMessage',
        ),
    ]
