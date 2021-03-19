from django.conf import settings


def enable_weni_layout(request):

    host, _ = request.get_host().split(":")

    return {"use_weni_layout": host.endswith(settings.WENI_DOMAINS["weni"])}
