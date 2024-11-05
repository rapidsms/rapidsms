from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("rapidsms", "0002_alter_contact_language"),
    ]

    operations = [
        migrations.DeleteModel(
            name="BackendMessage",
        ),
    ]
