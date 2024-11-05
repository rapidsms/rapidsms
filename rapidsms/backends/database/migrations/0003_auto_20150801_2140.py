from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("database", "0002_auto_20150710_1421"),
    ]

    operations = [
        migrations.AlterField(
            model_name="backendmessage",
            name="direction",
            field=models.CharField(
                db_index=True,
                max_length=1,
                choices=[("I", "Incoming"), ("O", "Outgoing")],
            ),
            preserve_default=True,
        ),
    ]
