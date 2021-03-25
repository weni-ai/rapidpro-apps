from django.conf import settings


def enable_weni_layout(request):

    host = request.get_host().split(":")[0]

    return {"use_weni_layout": host.endswith(settings.WENI_DOMAINS["weni"])}
