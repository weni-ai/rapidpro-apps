from django import forms
from django.utils.translation import ugettext_lazy as _

from temba.utils.uuid import uuid4

from weni.internal.external_services.views import BaseConnectView
from weni.internal.models import ExternalService


class ConnectView(BaseConnectView):
    class Form(BaseConnectView.Form):
        name = forms.CharField(
            max_length=256,
            label=_("Name"), help_text=_("Name")
        )
        app_key = forms.CharField(
            label=_("Omie App Key"), help_text=_("Omie App Key")
        )
        app_secret = forms.CharField(
            label=_("Omie App Secret"), help_text=_("Omie App Secret")
        )

        def clean(self):
            app_key = self.cleaned_data.get("app_key")
            if not app_key:
                raise forms.ValidationError(_("Invalid App Key"))
            
            app_secret = self.cleaned_data.get("app_secret")
            if not app_secret:
                raise forms.ValidationError(_("Invalid App Secret"))

    def form_valid(self, form):
        from .type import OmieType

        name = form.cleaned_data["name"]
        app_key = form.cleaned_data["app_key"]
        app_secret = form.cleaned_data["app_secret"]

        config = {
            OmieType.CONFIG_APP_KEY: app_key,
            OmieType.CONFIG_APP_SECRET: app_secret
        }

        self.object = ExternalService(
            uuid=uuid4(),
            org=self.org,
            external_service_type=OmieType.slug,
            config=config,
            name=name,
            created_by=self.request.user,
            modified_by=self.request.user,
        )

        self.object.save()
        return super().form_valid(form)
    
    form_class = Form
    template_name = "external_services/types/omie/connect.haml"
