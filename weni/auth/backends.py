import logging

from mozilla_django_oidc.auth import OIDCAuthenticationBackend

LOGGER = logging.getLogger("weni_django_oidc")


class WeniOIDCAuthenticationBackend(OIDCAuthenticationBackend):
    def verify_claims(self, claims):
        # validação de permissão
        verified = super(WeniOIDCAuthenticationBackend, self).verify_claims(claims)
        # is_admin = "admin" in claims.get("roles", [])
        return verified  # and is_admin # not checking for user roles from keycloak at this time

    def get_username(self, claims):
        username = claims.get("email")
        if username:
            return username
        return super(WeniOIDCAuthenticationBackend, self).get_username(claims=claims)

    def create_user(self, claims):
        # Override existing create_user method in OIDCAuthenticationBackend
        email = claims.get("email")
        username = self.get_username(claims)
        user = self.UserModel.objects.create_user(email, username)

        user.first_name = claims.get("given_name", "")
        user.last_name = claims.get("family_name", "")

        user.save()

        return user

    def update_user(self, user, claims):
        user.first_name = claims.get("given_name", "")
        user.last_name = claims.get("family_name", "")

        user.save()

        return user
