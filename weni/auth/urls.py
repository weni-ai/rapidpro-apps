from django.conf.urls import include, url
from weni.auth.views import check_user_legacy, org_choose

urlpatterns = [
    url(r"^oidc/", include("mozilla_django_oidc.urls")),
    url(r"^check-user-legacy/(?P<email>.*\\w+)/$", check_user_legacy, name="check-user-legacy"),
    url(
        r"^weni/org_choose/(?P<organization>[0-9a-fA-F]{8}-?)[0-9a-fA-F]{4}-?){3}[0-9a-fA-F]{12}",
        org_choose,
        name="weni-org-choose",
    ),
]
