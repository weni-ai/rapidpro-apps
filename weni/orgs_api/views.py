from django.shortcuts import get_object_or_404

from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action
from rest_framework.response import Response

from temba.orgs.models import Org


class OrgViewSet(GenericViewSet):
    permission = "orgs.org_api"
    lookup_field = "uuid"

    @action(detail=True, methods=["PATCH"])
    def is_suspended(self, request, uuid=None):
        org = get_object_or_404(Org, uuid=uuid)

        org.config["is_suspended"] = bool(request.data.get("is_suspended"))
        org.save()

        return Response(dict(is_suspended=org.config.get("is_suspended", False)))
