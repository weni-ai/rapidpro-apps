from django.db import connection


class ActiveContactsQuery:
    @classmethod
    def total(cls):
        with connection.cursor() as cursor:
            cursor.execute(
                "select count(distinct urn.contact_id) from msgs_msg msg "
                "inner join contacts_contacturn urn on urn.id = msg.contact_urn_id "
                "where not (msg.status = 'F');"
            )
            row = cursor.fetchone()
            return row[0]
