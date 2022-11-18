from rest_framework import mixins
from rest_framework.generics import get_object_or_404

from temba.tickets.models import Ticketer
from weni.internal.views import InternalGenericViewSet
from weni.internal.models import TicketerQueue
from weni.internal.tickets.serializers import TicketerSerializer, TicketerQueueSerializer


class TicketerViewSet(
    mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, InternalGenericViewSet
):
    serializer_class = TicketerSerializer
    queryset = Ticketer.objects.filter(is_active=True)
    lookup_field = "uuid"

    def perform_destroy(self, instance):
        instance.release(self.request.user)


class TicketerQueueViewSet(
    mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, InternalGenericViewSet
):
    serializer_class = TicketerQueueSerializer
    queryset = TicketerQueue.objects
    lookup_field = "uuid"

    @property
    def _ticketer(self):
        sector_uuid = self.kwargs.get("ticketer_uuid")
        return get_object_or_404(Ticketer, config__sector_uuid=sector_uuid)

    def get_queryset(self):
        return super().get_queryset().filter(ticketer=self._ticketer)

    def perform_create(self, serializer):
        ticketer = self._ticketer

        serializer.save(
            ticketer=ticketer,
            org=ticketer.org,
            created_by=self.request.user,
            modified_by=self.request.user,
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.get("partial", False)
        if not partial:
            self.http_method_not_allowed(request, *args, **kwargs)

        return super().update(request, *args, **kwargs)
