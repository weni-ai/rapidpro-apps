# Generated by Django 2.2.20 on 2021-06-24 19:31

from django.db import migrations, models

SQL = """
----------------------------------------------------------------------
-- Determines the (mutually exclusive) system label for a broadcast record
----------------------------------------------------------------------
CREATE OR REPLACE FUNCTION temba_broadcast_determine_system_label(_broadcast msgs_broadcast) RETURNS CHAR(1) AS $$
BEGIN
  IF _broadcast.schedule_id IS NOT NULL THEN
    RETURN 'E';
  END IF;

  IF _broadcast.status = 'Q' THEN
    RETURN 'O';
  END IF;

  RETURN NULL; -- does not match any label
END;
$$ LANGUAGE plpgsql;

DROP INDEX msgs_broadcasts_org_created_id_where_active
"""


class Migration(migrations.Migration):

    dependencies = [
        ("msgs", "0149_auto_20210621_1926"),
    ]

    operations = [
        migrations.AlterField(
            model_name="broadcast",
            name="is_active",
            field=models.BooleanField(default=True, null=True),
        ),
        migrations.AddIndex(
            model_name="broadcast",
            index=models.Index(fields=["org", "-created_on", "-id"], name="msgs_broadcasts_org_created_id"),
        ),
        migrations.RunSQL(SQL),
    ]