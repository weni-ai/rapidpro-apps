from rest_framework import viewsets
from rest_framework import generics
from rest_framework import mixins
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError

from django.contrib.auth.models import User
from django.db.models import Count, Prefetch, Q
from django.urls import reverse
from django.http import JsonResponse

from temba.api.v2.views_base import BaseAPIView, ListAPIMixin
from temba.contacts.models import Contact, ContactGroup
from temba.classifiers.models import Classifier
from temba.orgs.models import Org

from .serializers import ClassifierSerializer, ClassifierDeleteSerializer
from weni.internal.views import InternalGenericViewSet


class ClassifierEndpoint(viewsets.ModelViewSet, InternalGenericViewSet):

    serializer_class = ClassifierSerializer
    lookup_field = "uuid"

    def get_queryset(self):

        is_active_possibilities = {
            "True": True,
            "False": False,
            "true": True,
            "false": False,
        }

        org_uuid = self.request.query_params.get("org_uuid")
        is_active = is_active_possibilities.get(self.request.query_params.get("is_active"))
        classifier_type = self.request.query_params.get("classifier_type")

        queryset = Classifier.objects.all()

        filters = {}

        if org_uuid is not None:
            try:
                org = Org.objects.get(uuid=org_uuid)
                filters["org"] = org
            except Org.DoesNotExist:
                raise ValidationError(detail="Org does not exist")

        if is_active is not None:
            try:
                filters["is_active"] = is_active
            except ValueError:
                raise ValidationError(detail="is_active cannot be null")

        if classifier_type is not None:
            filters["classifier_type"] = classifier_type

        return queryset.filter(**filters)

    def create(self, request):
        serializer = ClassifierSerializer(data=request.data)

        if not serializer.is_valid():
            return JsonResponse(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()

        return JsonResponse(data=serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, uuid=None):

        try:
            classifier = Classifier.objects.get(uuid=uuid)
        except Classifier.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return JsonResponse(data=self.get_serializer(classifier).data, status=status.HTTP_200_OK)

    def destroy(self, request, uuid=None):

        data = {
            "uuid": uuid,
            "user": request.query_params.get("user_email"),
        }

        serializer = ClassifierDeleteSerializer(data=data)
        if not serializer.is_valid():
            return JsonResponse(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        classifier = Classifier.objects.get(uuid=uuid)
        classifier.release(serializer.validated_data.get("user"))

        return Response(status=status.HTTP_200_OK)
