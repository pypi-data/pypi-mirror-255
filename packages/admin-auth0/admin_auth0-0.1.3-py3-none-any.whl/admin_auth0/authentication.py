import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import Group
from authlib.integrations.django_client import OAuth


oauth = OAuth()

oauth.register(
    'auth0',
    client_id=settings.DJANGO_ADMIN_AUTH0_CLIENT_ID,
    client_secret=settings.DJANGO_ADMIN_AUTH0_CLIENT_SECRET,
    authorize_params={
        'audience': settings.DJANGO_ADMIN_AUTH0_AUDIENCE,
        'scope': settings.DJANGO_ADMIN_AUTH0_SCOPE,
    },
    server_metadata_url=f'https://{settings.DJANGO_ADMIN_AUTH0_DOMAIN}/.well-known/openid-configuration',
)


class DjangoSSOAuthBackend(BaseBackend):
    def get_user(self, user_id):
        cls = get_user_model()
        return cls.objects.get(pk=user_id)

    @staticmethod
    def get_or_create_user_by_email(user_email):
        cls = get_user_model()
        return cls.objects.get_or_create(email=user_email)

    def authenticate(self, request, **kwargs):
        if kwargs.get('username') and kwargs.get('password'):
            return None

        token = kwargs.get('token')

        if not token:
            return None

        user, is_created = self.get_or_create_user_by_email(token['userinfo']['email'])
        self.update_user_permissions(user, token['access_token'])
        return user

    @staticmethod
    def parse_token(token):
        return jwt.decode(token, options={'verify_signature': False})

    @staticmethod
    def update_user_groups(user, permissions):
        groups = Group.objects.filter(name__in=permissions)
        user.groups.set(groups)

    def update_user_permissions(self, user, token):
        token_data = self.parse_token(token)

        if settings.DJANGO_ADMIN_AUTH0_AUDIENCE not in token_data['aud']:
            return

        permissions = token_data.get('permissions', [])

        if not permissions:
            return

        user.is_staff = True
        user.is_superuser = settings.DJANGO_ADMIN_AUTH0_SUPER_ADMIN_ROLE in permissions
        user.save()
        self.update_user_groups(user, permissions)
        return
