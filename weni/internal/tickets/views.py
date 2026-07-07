from rest_framework import mixins
from rest_framework.exceptions import NotFound
from rest_framework.generics import get_object_or_404

from temba.tickets.models import Ticketer
from weni.internal.views import InternalGenericViewSet
from weni.internal.models import TicketerQueue
from weni.internal.tickets.serializers import (
    TicketerConfigSerializer,
    TicketerSerializer,
    TicketerQueueSerializer,
)


class SectorViewSet(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    InternalGenericViewSet,
):
    serializer_class = TicketerConfigSerializer
    queryset = Ticketer.objects.filter(is_active=True)
    lookup_field = "uuid"

    def get_object(self):
        sector_uuid = self.kwargs.get("uuid")
        return get_object_or_404(self.queryset, config__sector_uuid=sector_uuid)

    def perform_destroy(self, instance):
        instance.release(self.request.user)


class TicketerViewSet(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    InternalGenericViewSet,
):
    serializer_class = TicketerSerializer
    queryset = Ticketer.objects.filter(is_active=True)
    lookup_field = "uuid"

    def perform_destroy(self, instance):
        instance.release(self.request.user)


class TicketerQueueViewSet(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    InternalGenericViewSet,
):
    serializer_class = TicketerQueueSerializer
    queryset = TicketerQueue.objects
    lookup_field = "queue_uuid"
    lookup_url_kwarg = "queue_uuid"

    def _get_project_uuid(self):
        return self.request.data.get("project_uuid") or self.request.query_params.get("project_uuid")

    @property
    def _ticketer(self):
        sector_uuid = self.kwargs.get("ticketer_uuid")
        project_uuid = self._get_project_uuid()
        filters = {"is_active": True, "config__sector_uuid": sector_uuid}
        if project_uuid:
            filters["org__proj_uuid"] = project_uuid
        return get_object_or_404(Ticketer, **filters)

    def get_queryset(self):
        return super().get_queryset().filter(is_active=True, ticketer=self._ticketer)

    def get_object(self):
        queryset = self.get_queryset()
        lookup_value = self.kwargs.get(self.lookup_url_kwarg or self.lookup_field)

        obj = queryset.filter(**{self.lookup_field: lookup_value}).first()
        if obj is None:
            obj = queryset.filter(uuid=lookup_value).first()
        if obj is None:
            raise NotFound()

        self.check_object_permissions(self.request, obj)
        return obj

    def perform_create(self, serializer):
        ticketer = self._ticketer

        serializer.save(
            ticketer=ticketer,
            org=ticketer.org,
            created_by=self.request.user,
            modified_by=self.request.user,
        )

    def perform_update(self, serializer):
        serializer.save(modified_by=self.request.user)

    def update(self, request, *args, **kwargs):
        partial = kwargs.get("partial", False)
        if not partial:
            self.http_method_not_allowed(request, *args, **kwargs)

        return super().update(request, *args, **kwargs)

    def perform_destroy(self, instance):
        instance.release()
