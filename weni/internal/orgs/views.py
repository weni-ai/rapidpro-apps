from rest_framework.mixins import CreateModelMixin

from weni.internal.views import InternalGenericViewSet
from weni.internal.orgs.serializers import TemplateOrgSerializer


class TemplateOrgViewSet(CreateModelMixin, InternalGenericViewSet):
    serializer_class = TemplateOrgSerializer
