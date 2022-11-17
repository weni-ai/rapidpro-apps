from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.http import JsonResponse

from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import viewsets
from rest_framework import status
from rest_framework.pagination import PageNumberPagination

from weni.internal.views import InternalGenericViewSet
from temba.channels.models import Channel

from .serializers import ChannelSerializer, CreateChannelSerializer, ChannelWACSerializer

User = get_user_model()

class ChannelEndpoint(viewsets.ModelViewSet, InternalGenericViewSet):
    serializer_class = ChannelSerializer
    lookup_field = "uuid"

    def get_queryset(self):
        channel_type = self.request.query_params.get("channel_type")
        org = self.request.query_params.get("org")

        queryset = Channel.objects.all()

        if channel_type is not None:
            return queryset.filter(channel_type=channel_type)

        if org is not None:
            return queryset.filter(org__uuid=org)

        return queryset

    def retrieve(self, request, uuid=None):
        try:
            channel = Channel.objects.get(uuid=uuid)
        except Channel.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return JsonResponse(data=self.get_serializer(channel).data, status=status.HTTP_200_OK)

    def create(self, request):
        serializer = CreateChannelSerializer(data=request.data)

        if not serializer.is_valid():
            return JsonResponse(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()

        return JsonResponse(data=serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, uuid=None):
        channel = get_object_or_404(Channel, uuid=uuid)
        user = get_object_or_404(User, email=request.data.get("user"))

        channel.release(user)

        return Response(status=status.HTTP_200_OK)

    @action(methods=["POST"], detail=False)
    def create_wac(self, request):
        serializer = ChannelWACSerializer(data=request.data)

        if not serializer.is_valid():
            return JsonResponse(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()

        return JsonResponse(data=serializer.data, status=status.HTTP_200_OK)
