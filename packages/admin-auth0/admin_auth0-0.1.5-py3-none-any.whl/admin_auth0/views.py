import logging
from urllib.parse import quote_plus
from urllib.parse import urlencode
from urllib.parse import urljoin

from authlib.integrations.base_client.errors import OAuthError
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.shortcuts import redirect
from django.urls import reverse

from admin_auth0.authentication import oauth

logger = logging.getLogger(__name__)


def custom_login(request):
    return oauth.auth0.authorize_redirect(request, urljoin(settings.BACKEND_HOST, reverse('callback')))


def callback(request):
    try:
        token = oauth.auth0.authorize_access_token(request)
    except OAuthError as error:
        logger.info({'error': error, 'message': 'Failed to fetch token'})
    else:
        user = authenticate(request, token=token)
        login(request, user)
    return redirect(urljoin(settings.BACKEND_HOST, reverse('admin:index')))


def logout(request):
    request.session.clear()

    return redirect(
        f'https://{settings.DJANGO_ADMIN_AUTH0_DOMAIN}/v2/logout?'
        + urlencode(
            {
                'returnTo': urljoin(settings.BACKEND_HOST, reverse('admin:index')),
                'client_id': settings.DJANGO_ADMIN_AUTH0_CLIENT_ID,
            },
            quote_via=quote_plus,
        ),
    )
