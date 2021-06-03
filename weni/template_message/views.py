from temba.api.v2.views_base import BaseAPIView, WriteAPIMixin
from temba.templates.models import TemplateTranslation
from weni.template_message.serializers import TemplateMessageSerializers


class TemplateMessageEndpoint(WriteAPIMixin, BaseAPIView):

    """
    ## Create Template Message

    A **POST** can be used to create a new template message

    * **channel** - the channel UUID.
    * **content** - a text field, can contain multiple characters and words.
    * **name** - specific identifier for the template(welcome, schedule, etc)
    * **language** - 3 caracters code(por, eng, fra, etc..)
    * **country** - 2 caracters code(BR, PT, US, etc...)
    * **variable_count** - number of variables in your template.
    * **status** - the template status.
        * A - approved
        * P - pending
        * R - rejected
        * U - unsupported language
    * **fb_namespace** - namespace of Facebook(this field is not required)
    * **namespace** - ...

    Example:

        POST /api/v2/template_messages.json
        {
            "channel": "8b504687-a145-4737-b13d-ed179b39a1e8",
            "content": "Hello, this is a example of template message content...",
            "name": "chegada_lead_whatsapp",
            "language": "por",
            "country": "BR",
            "variable_count": 1,
            "status": "A",
            "fb_namespace": "36ffbf5c_482f_4943_a0cd_be1412349e74",
            "namespace": "Weni"
        }
    """

    permission = "templates.template_api"
    model = TemplateTranslation
    write_serializer_class = TemplateMessageSerializers
    serializer_class = TemplateMessageSerializers
