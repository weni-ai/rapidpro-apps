from rest_framework import routers

from weni.internal.orgs.views import TemplateOrgViewSet, OrgViewSet


router = routers.DefaultRouter()
router.register(r"template-orgs", TemplateOrgViewSet, basename="template-orgs")
router.register(r"orgs", OrgViewSet, basename="orgs")

urlpatterns = router.urls
