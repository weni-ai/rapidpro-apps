"""
Internal route registration

To register a new app, import it as:
    from weni.internal.projects.urls import urlpatterns as projects_urls

After that concatenate its value in internal_urlpatterns like:
    internal_urlpatterns += projects_urls
"""

from django.urls import path, include

from weni.internal.flows.urls import urlpatterns as flows_urls


internal_urlpatterns = []
internal_urlpatterns += flows_urls


urlpatterns = [path("internals/", include(internal_urlpatterns))]
