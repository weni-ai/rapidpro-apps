# Generated by Django 2.2.4 on 2020-08-07 17:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("orgs", "0067_populate_multi_orgs"),
    ]

    operations = [
        migrations.AddField(model_name="org", name="plan_end", field=models.DateTimeField(null=True),),
    ]
