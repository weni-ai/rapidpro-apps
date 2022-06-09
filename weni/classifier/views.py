from django.db.models import Count, Prefetch, Q
from django.urls import reverse
from django.http import JsonResponse
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from rest_framework import viewsets
from rest_framework import generics
from rest_framework import mixins
from .serializers import ChannelSerializer

from temba.api.v2.views_base import BaseAPIView, ListAPIMixin
from temba.contacts.models import Contact, ContactGroup
from temba.orgs.models import Org
from temba.flows.models import FlowRun
from temba.utils import str_to_bool
from rest_framework import status

from django.contrib.auth.models import User

from weni.grpc.classifier.serializers import ClassifierProtoSerializer
from temba.classifiers.models import Classifier


class ClassifierServiceViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    generics.GenericService
    ):
    pass

class ClassifierEndpoint(ClassifierServiceViewSet):

    serializer_class = ClassifierProtoSerializer
    queryset = Classifier.objects.all()
    lookup_field = "uuid"

    def list(self, request, *args, **kwargs):
        org = self.get_org_object(request.data.get("org_uuid"), "uuid")

        query = {"classifier_type": request.data.get("classifier_type")} if request.data.get("classifier_type") else {}

        classifiers = org.classifiers.filter(**query, is_active=request.data.get("is_active"))
        serializer = ClassifierProtoSerializer(classifiers, many=True)

        for message in serializer.message:
            yield message

    def delete(self, request, *args, **kwargs):
        classifier = self._get_object(Classifier, request.data.get("uuid"), "uuid")
        user = self.get_user_object(request.data.get("user_email"), "email")
        classifier.release(user)