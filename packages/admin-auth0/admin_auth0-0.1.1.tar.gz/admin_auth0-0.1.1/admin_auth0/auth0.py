import environ

env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False)
)

AUTH0_AUDIENCE = env('AUTH0_AUDIENCE')
AUTH0_CLIENT_ID = env('AUTH0_CLIENT_ID')
AUTH0_CLIENT_SECRET = env('AUTH0_CLIENT_SECRET')
AUTH0_DOMAIN = env('AUTH0_DOMAIN', default='abex-internal.eu.auth0.com')
AUTH0_SCOPE = env('AUTH0_SCOPE', default='openid profile email')
AUTH0_SUPER_ADMIN_ROLE = env('AUTH0_SUPER_ADMIN_ROLE', default='Super Admin')
