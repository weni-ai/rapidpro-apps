from django_grpc_framework import generics
from django_grpc_framework import mixins

from weni.grpc_central.services import AbstractService
from weni.classifier_grpc.serializers import ClassifierProtoSerializer


class ClassifierService(AbstractService, mixins.CreateModelMixin, generics.GenericService):

    serializer_class = ClassifierProtoSerializer

    def List(self, request, context):
        org = self.get_org_object(request.org_uuid, "uuid")

        query = {
            "classifier_type": request.classifier_type
        } if request.classifier_type else {}

        classifiers = org.classifiers.filter(**query)
        serializer = ClassifierProtoSerializer(classifiers, many=True)

        for message in serializer.message:
            yield message
