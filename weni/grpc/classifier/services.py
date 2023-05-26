from django_grpc_framework import generics
from django_grpc_framework import mixins

from temba.classifiers.models import Classifier
from weni.grpc.core.services import AbstractService
from weni.grpc.classifier.serializers import ClassifierProtoSerializer


class ClassifierService(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    generics.GenericService,
    AbstractService,
):
    serializer_class = ClassifierProtoSerializer
    queryset = Classifier.objects.all()
    lookup_field = "uuid"

    def List(self, request, context):
        org = self.get_org_object(request.org_uuid, "uuid")

        query = {"classifier_type": request.classifier_type} if request.classifier_type else {}

        classifiers = org.classifiers.filter(**query, is_active=request.is_active)
        serializer = ClassifierProtoSerializer(classifiers, many=True)

        for message in serializer.message:
            yield message

    def Destroy(self, request, context):
        classifier = self._get_object(Classifier, request.uuid, "uuid")
        user = self.get_user_object(request.user_email, "email")
        classifier.release(user)
