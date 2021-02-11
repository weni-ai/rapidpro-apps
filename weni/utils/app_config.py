from temba.api.v2.urls import urlpatterns
from temba.api.v2.views import ExplorerView


def update_urlpatterns(app_urls):
    def context_data(cls, **kwargs):
        ctx = context_func(cls, **kwargs)
        added = []
        for url in app_urls:
            view = url.callback.view_class
            view_id = id(view)
            if view_id not in added:
                ctx["endpoints"].append(view.get_read_explorer())
                added.append(view_id)
        return ctx

    urlpatterns.extend(app_urls)
    context_func = ExplorerView.get_context_data
    ExplorerView.get_context_data = context_data
