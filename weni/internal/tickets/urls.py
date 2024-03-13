from rest_framework_nested import routers

from weni.internal.tickets.views import SectorViewSet, TicketerViewSet, TicketerQueueViewSet


router = routers.SimpleRouter()
router.register(r"sectors", SectorViewSet, basename="sector")

router.register(r"ticketers", TicketerViewSet, basename="ticketer")

queues_router = routers.NestedSimpleRouter(router, "ticketers", lookup="ticketer")
queues_router.register("queues", TicketerQueueViewSet, "ticketer-queues")


urlpatterns = router.urls
urlpatterns += queues_router.urls
