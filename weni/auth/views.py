import json

from django.conf import settings
from django.contrib.auth.models import User
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from mozilla_django_oidc.views import OIDCAuthenticationRequestView
from temba.orgs.models import Org


@csrf_exempt
def check_user_legacy(request, email: str):  # pragma: no cover
    try:
        if settings.SECRET_KEY_CHECK_LEGACY_USER:
            prefix, token = request.headers.get("Authorization").split()
            if prefix.lower() != "bearer" or token != settings.SECRET_KEY_CHECK_LEGACY_USER:

                return HttpResponse(status=404)
    except AttributeError:
        return HttpResponse(status=404)

    if request.method == "GET":
        user = get_object_or_404(User, email=email)
        return JsonResponse(
            {
                "id": user.pk,
                "username": user.username,
                "email": user.email,
                "firstName": user.first_name,
                "lastName": user.last_name,
                "enabled": user.is_active,
                "emailVerified": user.is_active,
                "attributes": {},
                "roles": [],
                "groups": [],
            }
        )
    elif request.method == "POST":
        user = get_object_or_404(User, username=email)
        body_unicode = request.body.decode("utf-8")
        body = json.loads(body_unicode)
        user.check_password(raw_password=body.get("password"))
        return JsonResponse({}) if user else Http404()
    return HttpResponse(status=404)


class WeniAuthenticationRequestView(OIDCAuthenticationRequestView):
    def get(self, request, organization=None):
        response = super().get(request)
        if organization:
            org = get_object_or_404(Org, uuid=organization)
            self.request.session["org_id"] = org.pk
        return response
