from django.conf.urls import include, url
from django.urls import path

from weni.auth.views import (
    check_user_legacy,
    WeniAuthenticationRequestView,
    OrgHomeRedirectView,
    FlowEditorRedirectView,
)

urlpatterns = [
    url(r"^oidc/", include("mozilla_django_oidc.urls")),
    url(r"^check-user-legacy/(?P<email>.*\\w+)/$", check_user_legacy, name="check-user-legacy"),
    path("weni/<uuid:organization>/authenticate", WeniAuthenticationRequestView.as_view(), name="weni-authenticate",),
    path(
        "weni/<uuid:organization>/flow/<uuid:uuid>/editor", FlowEditorRedirectView.as_view(), name="weni-flow-editor",
    ),
    path("weni/<uuid:organization>/config", OrgHomeRedirectView.as_view(), name="weni-org-home"),
]
