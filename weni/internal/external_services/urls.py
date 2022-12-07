from django.conf.urls import include, url

from weni.internal.models import ExternalService
from weni.internal.external_services.views import ExternalServiceCRUDL

service_urls = []
for external_service_type in ExternalService.get_types():
    urls = external_service_type.get_urls()
    for u in urls:
        u.name  = "external_service.types.%s.%s" % (external_service_type.slug, u.name)

    if urls:
        service_urls.append(url("^%s/" % external_service_type.slug, include(urls)))

urlpatterns = [
    url(r"^", include(ExternalServiceCRUDL().as_urlpatterns())),
    url(r"^external_services/types/", include(service_urls))
]
