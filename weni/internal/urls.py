"""
Internal route registration

To register a new app, import it as:
    from weni.internal.orgs.urls import urlpatterns as orgs_urls

After that concatenate its value in internal_urlpatterns like:
    internal_urlpatterns += orgs_urls
"""

from django.urls import path, include

from weni.internal.orgs.urls import urlpatterns as orgs_urls
from weni.internal.flows.urls import urlpatterns as flows_urls
from weni.internal.users.urls import urlpatterns as users_urls
from weni.internal.tickets.urls import urlpatterns as tickets_urls


internal_urlpatterns = []
internal_urlpatterns += orgs_urls
internal_urlpatterns += flows_urls
internal_urlpatterns += users_urls
internal_urlpatterns += tickets_urls

urlpatterns = [path("internals/", include(internal_urlpatterns))]
