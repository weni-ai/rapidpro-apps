from rest_framework import mixins
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from temba.globals.models import Global
from temba.orgs.models import Org
from weni.internal.views import InternalGenericViewSet
from weni.internal.globals.serializers import GlobalSerializer


class GlobalViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    InternalGenericViewSet,
):
    serializer_class = GlobalSerializer
    lookup_field = "uuid"

    def get_queryset(self):
        queryset = Global.objects.filter(is_active=True)
        org = self.request.query_params.get("org")

        try:
            org_object = Org.objects.get(uuid=org)
            queryset = queryset.filter(org=org_object)
            return queryset

        except Org.DoesNotExist as error:
            raise ValidationError(detail={"message": str(error)})

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)

        self.perform_create(serializer.validated_data)

        headers = self.get_success_headers(serializer.data)

        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, validated_data_list):
        self.get_serializer().create_many(validated_data_list)
