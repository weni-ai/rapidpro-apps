from rest_framework import mixins

from temba.globals.models import Global
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
    queryset = Global.objects.filter(is_active=True)
    lookup_field = "uuid"
