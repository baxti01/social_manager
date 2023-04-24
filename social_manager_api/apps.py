from django.apps import AppConfig
from django.db.models.signals import post_delete


class SocialManagerApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'social_manager_api'

    def ready(self):
        from social_manager_api import signals
        post_delete.connect(signals.delete_files)
