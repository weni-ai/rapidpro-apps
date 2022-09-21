from rest_framework import mixins

from temba.tickets.models import Ticketer
from weni.internal.views import InternalGenericViewSet
from weni.internal.tickets.serializers import TicketerSerializer


class TicketerViewSet(
    mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, InternalGenericViewSet
):
    serializer_class = TicketerSerializer
    queryset = Ticketer.objects.filter(is_active=True)
    lookup_field = "uuid"

    def perform_destroy(self, instance):
        instance.release(self.request.user)
