from django.db import migrations

INDEX_NAME = "channel_stats_msg_sent_on_idx"
SQL_INDEX = f"""
CREATE INDEX {INDEX_NAME} ON "msgs_msg" ("contact_id", "sent_on" DESC)
       WHERE "sent_on" IS NOT NULL
         AND "direction" = 'O';
"""


class Migration(migrations.Migration):
    dependencies = [("msgs", "0138_remove_broadcast_recipient_count")]

    operations = [migrations.RunSQL(SQL_INDEX, f'DROP INDEX IF EXISTS "{INDEX_NAME}";')]
