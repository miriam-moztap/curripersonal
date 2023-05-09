from decouple import config

from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=False, cast=bool)

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': config('DB_BACKEND_PRODUCTION'),
        'NAME': config('DB_NAME_PRODUCTION'),
        'USER': config('DB_USERNAME_PRODUCTION'),
        'PASSWORD': config('DB_PASSWORD_PRODUCTION'),
        'PORT': config('DB_PORT_PRODUCTION'),
        'HOST': config('DB_HOST_PRODUCTION')
    }
}


