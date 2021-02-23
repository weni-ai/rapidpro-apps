import grpc

from django_grpc_framework import generics, mixins

from weni.user_grpc.serializers import OrgProtoSerializer

class UserService(generics.GenericService, mixins.ListModelMixin):
    
    def List(self, request, context):
        ...
