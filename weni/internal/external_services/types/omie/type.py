from django.utils.translation import ugettext_lazy as _

from weni.internal.external_services.views import ExternalServiceType
from weni.internal.external_services.types.omie import ConnectView

class OmieType(ExternalServiceType):
    """
    Type for using omie as a external service
    """

    CONFIG_APP_KEY = "app_key"
    CONFIG_APP_SECRET = "app_secret"
    
    name = "Omie"
    slug = "omie"
    icon = "icon-power-cord"
    
    connect_view = ConnectView
    connect_blurb = _("omie external service")

    def is_available_to(self, user):
        return True
