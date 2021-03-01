import grpc

from temba.orgs.models import Org
from django.core import exceptions


class AbstractService:
    def get_org_object_pk(self, pk: int) -> Org:
        return self.get_org_object(pk)

    def get_org_object(self, value: str, query_parameter: str = "pk") -> Org:
        return self._get_object(Org, value, query_parameter)

    def _get_object(self, model, value: str, query_parameter: str = "pk"):

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