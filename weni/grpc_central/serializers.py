from django.core import exceptions
from django.db import models
from django.contrib.auth.models import User
from django_grpc_framework import proto_serializers

from temba.orgs.models import Org


class SerializerUtils:
    
    @classmethod
    def get_user_object(cls, **kwargs) -> User:
        return cls._get_object(User, **kwargs)
    
    @classmethod
    def get_org_object(cls, **kwargs) -> Org:
        return cls._get_object(Org, **kwargs)
    
    @classmethod
    def _get_object(cls, model, **kwargs) -> models.Model:
        
        values = ", ".join(kwargs.values())
        
        try:
            return model.objects.get(**kwargs)
        except model.DoesNotExist:
            cls.raises_not_found(model.__name__, values)

    @classmethod
    def raises_not_found(cls, model_name, values):
        if not values:
            values = "None"            
        raise proto_serializers.ValidationError(f"{model_name}: ({values}) not found!")
