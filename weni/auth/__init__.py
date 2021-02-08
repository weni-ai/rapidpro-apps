from .backends import WeniOIDCAuthenticationBackend as oidc  # noqa: F401

default_app_config = "weni.auth.apps.AuthConfig"
