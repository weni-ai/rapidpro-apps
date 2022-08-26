from rest_framework import routers

from weni.internal.orgs.views import TemplateOrgViewSet


router = routers.DefaultRouter()
router.register(r"template-orgs", TemplateOrgViewSet, basename="template-orgs")


urlpatterns = router.urls
