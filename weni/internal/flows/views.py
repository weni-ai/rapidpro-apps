from rest_framework.mixins import CreateModelMixin, ListModelMixin
from rest_framework.exceptions import NotFound
from rest_framework.pagination import PageNumberPagination

from weni.internal.views import InternalGenericViewSet
from weni.internal.flows.serializers import FlowSerializer, FlowListSerializer

from temba.flows.models import Flow


class FlowPagination(PageNumberPagination):
    page_size_query_param = "page_size"
    max_page_size = 20


class FlowViewSet(CreateModelMixin, InternalGenericViewSet, ListModelMixin):
    serializer_class = FlowSerializer
    pagination_class = FlowPagination

    def get_queryset(self):
        serializer = self.get_serializer(data=self.request.query_params.dict())
        serializer.is_valid(raise_exception=True)

        queryset = Flow.objects.filter(
            org=serializer.validated_data.get("project").org,
            is_active=True,
        ).exclude(is_archived=True)

        flow_name = serializer.validated_data.get("flow_name")
        if flow_name:
            queryset = queryset.filter(name__icontains=flow_name)

        if queryset:
            return queryset

        raise NotFound()


class ProjectFlowsViewSet(ListModelMixin, InternalGenericViewSet):
    serializer_class = FlowListSerializer

    def get_queryset(self):
        serializer = self.get_serializer(data=self.request.query_params.dict())
        serializer.is_valid(raise_exception=True)

        queryset = Flow.objects.filter(
            name__icontains=serializer.validated_data.get("flow_name"),
            org=serializer.validated_data.get("project").org,
            is_active=True,
        ).exclude(is_archived=True)[:20]

        if queryset:
            return queryset

        raise NotFound()
