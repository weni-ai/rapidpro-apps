from django.core import exceptions
from django.contrib.auth.models import User

import grpc

from temba.orgs.models import Org


class AbstractService:
    def get_user_object(self, value, query_parameter: str = "pk"):
        return self._get_object(User, value, query_parameter)

    def get_org_object(self, value, query_parameter: str = "pk") -> Org:
        return self._get_object(Org, value, query_parameter)

    def _get_object(self, model, value, query_parameter: str):
        query = {query_parameter: value}

        try:
            return model.objects.get(**query)
        except model.DoesNotExist:
            self.raises_not_fount(model.__name__, value)
        except exceptions.ValidationError:
            self.raises_not_fount(model.__name__, value)

    def raises_not_fount(self, model_name, value):
        if not value:
            value = "None"
        self.context.abort(grpc.StatusCode.NOT_FOUND, f"{model_name}: {value} not found!")
