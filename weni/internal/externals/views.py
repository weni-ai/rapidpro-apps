from typing import TYPE_CHECKING

from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from weni.internal.authenticators import InternalOIDCAuthentication
from weni.internal.permissions import CanCommunicateInternally
from weni.internal.externals.serializers import ExternalServicesSerializer
from temba.externals.models import ExternalService


if TYPE_CHECKING:
    from rest_framework.request import Request


class ExternalServicesAPIView(APIView):
    authentication_classes = [InternalOIDCAuthentication]
    permission_classes = [IsAuthenticated, CanCommunicateInternally]
    pagination_class = None
    renderer_classes = [JSONRenderer]
    throttle_classes = []

    def post(self, request: "Request") -> Response:
        serializer = ExternalServicesSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, uuid=None):
        external_service = get_object_or_404(ExternalService, uuid=uuid)
        user = get_object_or_404(User, email=request.query_params.get("user"))

        external_service.release(user)

        return Response(status=status.HTTP_204_NO_CONTENT)
