from rest_framework.mixins import CreateModelMixin, ListModelMixin
from rest_framework.exceptions import NotFound

from weni.internal.views import InternalGenericViewSet
from weni.internal.flows.serializers import FlowSerializer, FlowListSerializer

from temba.flows.models import Flow


class FlowViewSet(CreateModelMixin, InternalGenericViewSet):
    serializer_class = FlowSerializer


class ProjectFlowsViewSet(ListModelMixin, InternalGenericViewSet):
    serializer_class = FlowListSerializer

    def get_queryset(self):
        serializer = self.get_serializer(data=self.request.query_params.dict())
        serializer.is_valid(raise_exception=True)

        queryset = Flow.objects.filter(
            name__icontains=serializer.validated_data.get("flow_name"),
            org=serializer.validated_data.get("org_uuid"),
            is_active=True,
        ).exclude(is_archived=True)[:20]

        if queryset:
            return queryset

        raise NotFound()
