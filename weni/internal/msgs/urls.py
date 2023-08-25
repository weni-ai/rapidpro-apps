from rest_framework import routers

from weni.internal.msgs.views import TemplateMessagesListView


router = routers.SimpleRouter()
router.register(
    r"template-messages", TemplateMessagesListView, basename="template-messages"
)

urlpatterns = router.urls
