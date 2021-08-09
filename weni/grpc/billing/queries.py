from datetime import datetime

from django.db import connection
from django.db.models import OuterRef, Subquery
from temba.contacts.models import Contact
from temba.msgs.models import Msg
from temba.orgs.models import Org


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

    @classmethod
    def detailed(cls, org_uuid: str, before: datetime, after: datetime):
        org = Org.objects.get(uuid=org_uuid)
        msg = (
            Msg.objects.filter(contact_urn__contact__pk=OuterRef("pk"), created_on__lte=before, created_on__gte=after)
            .exclude(status="F")
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
            .filter(org=org, msg__uuid__isnull=False,)
            .values(
                "uuid",
                "name",
                "msg__uuid",
                "msg__text",
                "msg__sent_on",
                "msg__direction",
                "channel__uuid",
                "channel__name"
            )
        )
