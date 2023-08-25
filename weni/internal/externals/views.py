from typing import TYPE_CHECKING

from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework import viewsets

from weni.internal.authenticators import InternalOIDCAuthentication
from weni.internal.permissions import CanCommunicateInternally
from weni.internal.externals.serializers import (
    ExternalServicesSerializer,
    UpdateExternalServicesSerializer,
    PromptSerializer
)
from temba.externals.models import ExternalService
from temba.externals.models import Prompt


if TYPE_CHECKING:
    from rest_framework.request import Request


class ExternalServicesAPIView(APIView):
    authentication_classes = [InternalOIDCAuthentication]
    permission_classes = [IsAuthenticated, CanCommunicateInternally]
    pagination_class = None
    renderer_classes = [JSONRenderer]
    throttle_classes = []

    def get_object(self):
        uuid = self.kwargs.get("uuid")
        return get_object_or_404(ExternalService, uuid=uuid)

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

    def patch(self, request, uuid=None):
        return self.update(request, uuid)

    def update(self, request, *args, **kwargs):
        external_service = self.get_object()
        serializer = UpdateExternalServicesSerializer(
            external_service, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def get(self, request, uuid=None):
        return self.retrieve(request, uuid)

    def retrieve(self, request, uuid=None):
        external_service = get_object_or_404(ExternalService, uuid=uuid)
        serializer = ExternalServicesSerializer(external_service)
        return Response(serializer.data)


class PromptViewSet(viewsets.ViewSet):
    authentication_classes = [InternalOIDCAuthentication]
    permission_classes = [IsAuthenticated, CanCommunicateInternally]
    pagination_class = None
    renderer_classes = [JSONRenderer]
    throttle_classes = []
    lookup_field = "uuid"

    def create(self, request, external_uuid=None):
        external_service = get_object_or_404(ExternalService, uuid=external_uuid)
        serializer = PromptSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(chat_gpt_service=external_service)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, external_uuid=None, uuid=None):
        queryset = Prompt.objects.filter(chat_gpt_service__uuid=external_uuid)
        prompt = get_object_or_404(queryset, uuid=uuid)
        serializer = PromptSerializer(prompt)
        return Response(serializer.data)

    def list(self, request, external_uuid=None):
        queryset = Prompt.objects.filter(chat_gpt_service__uuid=external_uuid)
        serializer = PromptSerializer(queryset, many=True)
        return Response(serializer.data)

    def destroy(self, request, external_uuid=None, uuid=None):
        queryset = Prompt.objects.filter(chat_gpt_service__uuid=external_uuid)

        try:
            prompt = queryset.get(uuid=uuid)
            prompt.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Prompt.DoesNotExist:
            return Response(
                data={"detail": f"Prompt {uuid} not found on flows"},
                status=status.HTTP_404_NOT_FOUND,
            )
