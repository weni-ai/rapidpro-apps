import json
import logging

from django.conf import settings
from django.contrib.auth.models import User
from django.http import Http404, HttpResponse, HttpResponseNotAllowed, JsonResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import RedirectView
from mozilla_django_oidc.views import OIDCAuthenticationRequestView, get_next_url
from weni.auth.decorators import org_choose

logger = logging.getLogger(__name__)


@csrf_exempt
def check_user_legacy(request, email: str):  # pragma: no cover
    try:
        prefix, token = request.headers.get("Authorization").split()
    except AttributeError:
        return HttpResponse(status=401)
    else:
        if prefix.lower() != "bearer" or token != settings.SECRET_KEY_CHECK_LEGACY_USER:
            logger.error(f"Invalid token: {token}")
            return HttpResponse(status=401)

    if request.method == "GET":
        user = get_object_or_404(User, username=email)
        return JsonResponse(
            {
                "username": user.username,
                "email": user.email,
                "firstName": user.first_name,
                "lastName": user.last_name,
                "enabled": user.is_active,
                "emailVerified": False,
                "attributes": {},
                "roles": [],
                "groups": [],
            }
        )
    elif request.method == "POST":
        user = get_object_or_404(User, username=email)
        body_unicode = request.body.decode("utf-8")
        body = json.loads(body_unicode)
        if user.check_password(raw_password=body.get("password")):
            return JsonResponse({})
        else:
            raise Http404("Wrong password")

    return HttpResponseNotAllowed(("GET", "POST"))


class WeniAuthenticationRequestView(OIDCAuthenticationRequestView):
    @org_choose
    def get(self, request):
        if request.user.is_authenticated:
            redirect_field_name = self.get_settings("OIDC_REDIRECT_FIELD_NAME", "next")
            next_url = get_next_url(request, redirect_field_name)
            return HttpResponseRedirect(next_url or settings.LOGIN_REDIRECT_URL)
        else:
            return super().get(request)


class OrgHomeRedirectView(RedirectView):
    pattern_name = "orgs.org_home"

    @org_choose
    def get(self, request):
        return super().get(request)


class FlowEditorRedirectView(RedirectView):
    pattern_name = "flows.flow_editor"

    @org_choose
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
