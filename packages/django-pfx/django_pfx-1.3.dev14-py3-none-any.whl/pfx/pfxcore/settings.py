from django.conf import settings

from . import default_settings


class PFXSettings:
    def __getattr__(self, attr):
        try:
            return getattr(settings, attr)
        except AttributeError:
            return getattr(default_settings, attr)
