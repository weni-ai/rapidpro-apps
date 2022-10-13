from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status

from temba.classifiers.models import Classifier
from temba.orgs.models import Org

from .serializers import ClassifierSerializer, ClassifierDeleteSerializer
from weni.internal.views import InternalGenericViewSet

User = get_user_model


class ClassifierEndpoint(viewsets.ModelViewSet, InternalGenericViewSet):

    serializer_class = ClassifierSerializer
    lookup_field = "uuid"
    queryset = Classifier.objects.all()

    def filter_queryset(self, queryset):
        org_uuid = self.request.query_params.get("org_uuid")
        is_active = self.request.query_params.get("is_active")
        classifier_type = self.request.query_params.get("classifier_type")

        filters = {}

        if org_uuid is not None:
            org = get_object_or_404(Org, uuid=org_uuid)
            filters["org"] = org

        if is_active is not None:
            try:
                filters["is_active"] = bool(int(is_active))
            except ValueError:
                return Response(status=status.HTTP_400_BAD_REQUEST)

        if classifier_type is not None:
            filters["classifier_type"] = classifier_type

        return queryset.filter(**filters)

    def destroy(self, request, uuid=None):

        data = {
            "uuid": uuid,
            "user": request.query_params.get("user_email"),
        }

        serializer = ClassifierDeleteSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        classifier = Classifier.objects.get(uuid=uuid)
        classifier.release(serializer.validated_data.get("user"))

        return Response(status=status.HTTP_200_OK)
