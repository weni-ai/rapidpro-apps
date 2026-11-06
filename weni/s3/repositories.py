from temba.tickets.models import Ticketer
from temba.tickets.types.zendesk.type import ZendeskType


def get_active_zendesk_ticketer(ticketer_uuid):
    """
    The only database access of the Zendesk file callback: one lookup by the unique uuid.
    """
    return Ticketer.objects.filter(uuid=ticketer_uuid, ticketer_type=ZendeskType.slug, is_active=True).first()
