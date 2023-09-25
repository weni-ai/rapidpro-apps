from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework import routers

from .views import ClassifierEndpoint

router = routers.SimpleRouter()
router.register("classifier", ClassifierEndpoint, basename="classifier")

urlpatterns = format_suffix_patterns(router.urls, allowed=["json", "api"])
