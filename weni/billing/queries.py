from django.db import connection
from datetime import datetime


class ActiveContactsQuery:
    @classmethod
    def total(cls, org_uuid: str, before: datetime, after: datetime) -> int:
        """Counts the number of active contacts (Contacts with any message between 'before' and 'after' with status different from FAILED) of a given org.

        Args:
            org_uuid (str): Org for search contacts
            before (datetime): Beginning of time range
            after (datetime): Ending of time range

        Returns:
            int: Total of active contacts in the given time range.
        """
        with connection.cursor() as cursor:
            cursor.execute(
                "select count(distinct urn.contact_id) from msgs_msg msg "
                "inner join contacts_contacturn urn on urn.id = msg.contact_urn_id "
                "inner join orgs_org org on org.id = msg.org_id "
                f"where org.uuid = '{org_uuid}' "
                f"and msg.created_on >= '{after}' "
                f"and msg.created_on < '{before}' "
                "and not (msg.status = 'F');"
            )
            row = cursor.fetchone()
            return row[0]
