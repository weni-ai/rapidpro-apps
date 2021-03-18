import regex
from django.conf import settings

URL_PATTERN = r"(?P<prefix>https?:\/\/)?(?P<domain>(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6})(?P<querystring>[-a-zA-Z0-9()!@:%_\+.~#?&\/\/=]*)?"


def enable_weni_layout(request):
    pattern = regex.compile(URL_PATTERN)
    match = pattern.match(request.get_host())

    if not match:
        return {}

    domain = match.groupdict()["domain"]
    return {"use_weni_layout": domain.endswith(settings.WENI_DOMAINS["weni"])}
