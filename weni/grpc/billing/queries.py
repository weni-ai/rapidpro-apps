from datetime import datetime

from django.db import connection
from django.db.models import OuterRef, Subquery, Q
from temba.contacts.models import Contact
from temba.msgs.models import Msg
from temba.orgs.models import Org


TOTAL_SQL = """
SELECT
	COUNT(DISTINCT urn.contact_id)
FROM contacts_contacturn AS urn
INNER JOIN orgs_org AS org
	ON org.id = urn.org_id
WHERE EXISTS (
	SELECT 1 FROM msgs_msg AS msg
	INNER JOIN channels_channel AS channel
		ON channel.id = msg.channel_id
	WHERE org.uuid = '%s'
    AND msg.created_on BETWEEN '%s' AND '%s'
	AND NOT (
		channel.channel_type IN ('EX', 'WWC') AND (
            (
                msg.text IN ('start','','pushinho')
                AND msg.direction = 'I'
            ) OR msg.direction = 'O'
        )
	)
	AND msg.contact_urn_id = urn.id
    AND NOT (msg.status = 'F')
);
"""


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
            cursor.execute(TOTAL_SQL % (org_uuid, after, before))
            row = cursor.fetchone()
            return row[0]

    @classmethod
    def detailed(cls, org_uuid: str, before: datetime, after: datetime):
        org = Org.objects.get(uuid=org_uuid)
        msg = (
            Msg.objects.filter(contact_urn__contact__pk=OuterRef("pk"), created_on__lte=before, created_on__gte=after)
            .exclude(status="F")
            .exclude(channel__channel_type__in=("EX", "WWC"), direction="O")
            .exclude(channel__channel_type__in=("EX", "WWC"), direction="I", text__in=("start", "", "pushinho"))
            .order_by("-created_on")
        )

        return (
            Contact.objects.annotate(
                msg__uuid=Subquery(msg.values("uuid")[:1]),
                msg__text=Subquery(msg.values("text")[:1]),
                msg__sent_on=Subquery(msg.values("sent_on")[:1]),
                msg__direction=Subquery(msg.values("direction")[:1]),
                channel__uuid=Subquery(msg.values("channel__uuid")[:1]),
                channel__name=Subquery(msg.values("channel__name")[:1]),
            )
            .filter(
                org=org,
                msg__uuid__isnull=False,
            )
            .values(
                "uuid",
                "name",
                "msg__uuid",
                "msg__text",
                "msg__sent_on",
                "msg__direction",
                "channel__uuid",
                "channel__name",
            )
        )
