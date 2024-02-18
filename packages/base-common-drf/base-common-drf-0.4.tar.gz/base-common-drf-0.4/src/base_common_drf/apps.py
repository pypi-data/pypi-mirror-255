from django.apps import AppConfig


class BaseCommonConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'base_common_drf'
    label = 'base_common_drf'
