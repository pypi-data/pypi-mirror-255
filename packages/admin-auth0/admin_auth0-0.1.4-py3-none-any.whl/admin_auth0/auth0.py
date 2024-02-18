import environ

env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False)
)

DJANGO_ADMIN_AUTH0_AUDIENCE = env('DJANGO_ADMIN_AUTH0_AUDIENCE', default='')
DJANGO_ADMIN_AUTH0_CLIENT_ID = env('DJANGO_ADMIN_AUTH0_CLIENT_ID', default='')
DJANGO_ADMIN_AUTH0_CLIENT_SECRET = env('DJANGO_ADMIN_AUTH0_CLIENT_SECRET', default='')
DJANGO_ADMIN_AUTH0_DOMAIN = env('DJANGO_ADMIN_AUTH0_DOMAIN', default='abex-internal.eu.auth0.com')
DJANGO_ADMIN_AUTH0_SCOPE = env('DJANGO_ADMIN_AUTH0_SCOPE', default='openid profile email')
DJANGO_ADMIN_AUTH0_SUPER_ADMIN_ROLE = env('DJANGO_ADMIN_AUTH0_SUPER_ADMIN_ROLE', default='Super Admin')
