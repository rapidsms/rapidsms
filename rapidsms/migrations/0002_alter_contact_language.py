from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("rapidsms", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="contact",
            name="language",
            field=models.CharField(
                help_text=(
                    "The language which this contact prefers to communicate in, "
                    "as a W3C language tag. If this field is left blank, "
                    "RapidSMS will default to the value in LANGUAGE_CODE."
                ),
                max_length=6,
                blank=True,
            ),
        ),
    ]
