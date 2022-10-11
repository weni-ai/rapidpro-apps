import imp
from typing import TYPE_CHECKING

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import exceptions

from weni.internal.views import InternalGenericViewSet
from weni.internal.users.serializers import UserAPITokenSerializer
from temba.api.models import APIToken


if TYPE_CHECKING:
    from rest_framework.request import Request


class UserViewSet(InternalGenericViewSet):

    @action(detail=False, methods=["GET"], url_path="api-token", serializer_class=UserAPITokenSerializer)
    def api_token(self, request: "Request", **kwargs):

        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        try:
            api_token = APIToken.objects.get(**serializer.validated_data)
        except APIToken.DoesNotExist:
            raise exceptions.PermissionDenied()

        return Response(dict(user=api_token.user.email, org=api_token.org.uuid, api_token=api_token.key))
