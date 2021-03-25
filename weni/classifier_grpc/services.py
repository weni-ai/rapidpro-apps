from django_grpc_framework import generics
from weni.grpc_central.services import AbstractService

from weni.classifier_grpc.serializers import ClassifierProtoSerializer


class ClassifierService(AbstractService, generics.GenericService):
    def List(self, request, context):
        org = self.get_org_object(request.org_uuid, "uuid")

        classifiers = org.classifiers.all()
        serializer = ClassifierProtoSerializer(classifiers, many=True)

        for message in serializer.message:
            yield message
