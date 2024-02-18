import sentry_sdk
from decouple import config

SENTRY_DSN = config("SENTRY_DSN", default=None)
SENTRY_ENABLE_TRACING = config("SENTRY_ENABLE_TRACING", cast=bool, default=False)


def register_plugin(app):
    if SENTRY_DSN:
        sentry_sdk.init(dsn=SENTRY_DSN, enable_tracing=SENTRY_ENABLE_TRACING)
