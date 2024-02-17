from django.apps import AppConfig


class BaseCommonConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'base_common'
    label = 'base_common'
