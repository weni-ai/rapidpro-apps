from rest_framework import routers

from weni.internal.tickets.views import TicketerViewSet


router = routers.DefaultRouter()
router.register(r"ticketers", TicketerViewSet, basename="ticketer")


urlpatterns = router.urls
