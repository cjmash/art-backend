from .base import *  # noqa: F403,F401
import os
DEBUG = True

ALLOWED_HOSTS = [os.environ.get('HOST_IP'),
    'art-api.andela.com'
]

CORS_ORIGIN_REGEX_WHITELIST = \
    (r'^(https?:\/\/)?(.+\.)?((andela\.com))', )
