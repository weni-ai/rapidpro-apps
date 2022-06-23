import json
import re

from django.http.response import HttpResponseRedirect
from django.db.models import Count, Prefetch, Q
from django.urls import reverse
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.test import RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.auth.models import User

from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import viewsets
from rest_framework import generics
from rest_framework import mixins
from rest_framework import exceptions
from rest_framework import status


from temba.contacts.models import Contact, ContactGroup
from temba.orgs.models import Org
from temba.flows.models import FlowRun
from temba.utils import str_to_bool
from temba.channels.models import Channel
from temba.channels.types import TYPES

from .serializers import ChannelSerializer, CreateChannelSerializer, ChannelWACSerializer


class ChannelEndpoint(viewsets.ModelViewSet):
    serializer_class = ChannelSerializer
    lookup_field = "uuid"

    def get_queryset(self):
        channel_type = self.request.query_params.get('channel_type')
        org = self.request.query_params.get('org')

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
        try:
            channel = Channel.objects.get(uuid=uuid)
        except Channel.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        channel.is_active = False
        channel.save()
        return Response(status=status.HTTP_200_OK)

    
    @action(methods=["POST"], detail=False)
    def create_wac(self, request):
        serializer = ChannelWACSerializer(data=request.data)
        
        if not serializer.is_valid():
            return JsonResponse(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        
        return JsonResponse(data=serializer.data, status=status.HTTP_200_OK)