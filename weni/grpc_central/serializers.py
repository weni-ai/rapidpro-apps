from django.core import exceptions
from django.db import models
from django.contrib.auth.models import User
from django_grpc_framework import proto_serializers

from temba.orgs.models import Org


class SerializerUtils:
    
    @classmethod
    def get_user_object(cls, value, query_parameter: str = "pk") -> User:
        return cls._get_object(User, value, query_parameter)
    
    @classmethod
    def get_org_object(cls, value, query_parameter: str = "pk") -> Org:
        return cls._get_object(Org, value, query_parameter)
    
    @classmethod
    def _get_object(cls, model, value, query_parameter: str) -> models.Model:

        query = {query_parameter: value}

        try:
            return model.objects.get(**query)
        except model.DoesNotExist:
            cls.raises_not_fount(model.__name__, value)
        except exceptions.ValidationError:
            cls.raises_not_fount(model.__name__, value)

    @classmethod
    def raises_not_fount(cls, model_name, value):
        if not value:
            value = "None"            
        raise proto_serializers.ValidationError(f"{model_name}: {value} not found!")
