from django.contrib.auth.models import User

import grpc
from django_grpc_framework import generics
from weni.org_grpc.serializers import (
    OrgProtoSerializer,
    OrgCreateProtoSerializer
)

from django_grpc_framework import mixins


class OrgService(generics.GenericService, mixins.ListModelMixin):

    def List(self, request, context):

        user = self.get_user(request)
        orgs = self.get_orgs(user)

        serializer = OrgProtoSerializer(orgs, many=True)

        for msg in serializer.message:
            yield msg

    def Create(self, request, context):
        serializer = OrgCreateProtoSerializer(message=request)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return serializer.message

    def get_user(self, request):
        user_email = request.user_email

        if not user_email:
            self.context.abort(grpc.StatusCode.NOT_FOUND,
                f"Email cannot be null")

        try:
            return User.objects.get(email=request.user_email)
        except User.DoesNotExist:
            self.context.abort(grpc.StatusCode.NOT_FOUND,
                f"User:{request.user_email} not found!")

    def get_orgs(self, user: User):
        return user.org_admins.union(user.org_viewers.all(),
            user.org_editors.all(), user.org_surveyors.all())
