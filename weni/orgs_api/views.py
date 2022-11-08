from django.shortcuts import get_object_or_404
from django.http import JsonResponse

from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action

from temba.orgs.models import Org

from .serializers import FlagOrgSerializer


class OrgViewSet(GenericViewSet):
    permission = "orgs.org_api"
    lookup_field = "uuid"

    @action(detail=True, methods=["PATCH"])
    def is_suspended(self, request, uuid=None):
        org = get_object_or_404(Org, uuid=uuid)

        org.config["is_suspended"] = bool(request.data.get("is_suspended"))
        org.save()

        return JsonResponse(dict(is_suspended=org.config.get("is_suspended", False)))

    @action(detail=True, methods=["POST", "DELETE"])
    def suspend_flag(self, request, uuid=None):
        org = get_object_or_404(Org, uuid=uuid)

        if request.method == "DELETE":
            if org.config.get("date_billing_expired"):
                org.config.pop("date_billing_expired")

            if org.config.get("date_org_will_suspend"):
                org.config.pop("date_org_will_suspend")

            org.save()
            return JsonResponse(data=dict(success=True), status=200)

        serializer = FlagOrgSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        for flag_name, date in serializer.data.items():
            org.config[flag_name] = date

        org.save()

        return JsonResponse(data=serializer.data, status=200)
