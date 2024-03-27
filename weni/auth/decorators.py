from functools import wraps

from django.shortcuts import get_object_or_404

from weni.internal.models import Project


def org_choose(func):
    @wraps(func)
    def wrapper(self, request, project=None, *args, **kwargs):
        if project:
            project = get_object_or_404(Project, project_uuid=project)
            org = project.org
            self.request.session["org_id"] = org.pk

        return func(self, request, *args, **kwargs)

    return wrapper
