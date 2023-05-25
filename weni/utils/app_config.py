from django.urls.resolvers import URLPattern, URLResolver
from temba.api.v2.views import ExplorerView
from importlib import import_module


def update_urlpatterns(app_urls, urls_module="temba.api.v2.urls"):
    def context_data(cls, **kwargs):
        ctx = context_func(cls, **kwargs)
        added = []
        for url in app_urls:
            if isinstance(url, URLPattern):
                if hasattr(url.callback, "view_class"):
                    view = url.callback.view_class
                else:
                    view = url.callback
                view_id = id(view)
                if view_id not in added and hasattr(view, "get_read_explorer"):
                    ctx["endpoints"].append(view.get_read_explorer())
                    added.append(view_id)
            elif isinstance(url, URLResolver):
                update_urlpatterns(url.url_patterns, urls_module)
        return ctx

    base_urls = import_module(urls_module)
    base_urls.urlpatterns.extend(app_urls)
    context_func = ExplorerView.get_context_data
    ExplorerView.get_context_data = context_data
