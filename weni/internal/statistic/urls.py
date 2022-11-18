from rest_framework import routers

from .views import StatisticEndpoint

router = routers.DefaultRouter()
router.register(r"statistic", StatisticEndpoint, basename="statistic")

urlpatterns = router.urls
