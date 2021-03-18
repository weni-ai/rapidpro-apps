from functools import wraps

from django.shortcuts import get_object_or_404

from temba.orgs.models import Org


def org_choose(func):
    @wraps(func)
    def wrapper(self, request, organization=None, *args, **kwargs):
        if organization:
            org = get_object_or_404(Org, uuid=organization)
            self.request.session["org_id"] = org.pk

        return func(self, request, *args, **kwargs)

    return wrapper
