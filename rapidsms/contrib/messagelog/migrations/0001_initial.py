# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("rapidsms", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Message",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                (
                    "direction",
                    models.CharField(
                        max_length=1, choices=[(b"I", b"Incoming"), (b"O", b"Outgoing")]
                    ),
                ),
                ("date", models.DateTimeField()),
                ("text", models.TextField()),
                (
                    "connection",
                    models.ForeignKey(
                        blank=True,
                        to="rapidsms.Connection",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),
                (
                    "contact",
                    models.ForeignKey(
                        blank=True,
                        to="rapidsms.Contact",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),
            ],
            options={},
            bases=(models.Model,),
        ),
    ]
