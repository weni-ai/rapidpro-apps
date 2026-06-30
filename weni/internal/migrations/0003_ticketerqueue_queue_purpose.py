from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("internal", "0002_project"),
    ]

    operations = [
        migrations.AddField(
            model_name="ticketerqueue",
            name="queue_purpose",
            field=models.TextField(blank=True, max_length=1000, null=True),
        ),
    ]
