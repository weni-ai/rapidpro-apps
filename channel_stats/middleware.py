from django.utils.deprecation import MiddlewareMixin

from .urls import urlpatterns


class APIExplorerV2(MiddlewareMixin):
    def process_view(self, request, view_func, view_args, views_kwargs):
        if request.resolver_match.view_name == "api.v2.explorer":
            def context_data(cls, **kwargs):
                nonlocal context_func
                ctx = context_func(cls, **kwargs)
                for url in urlpatterns:
                    ctx["endpoints"].append(url.callback.view_class.get_read_explorer())
                return ctx

            context_func = view_func.view_class.get_context_data
            view_func.view_class.get_context_data = context_data
