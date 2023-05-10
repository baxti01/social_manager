from django.apps import AppConfig


class SocialManagerApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'social_manager_api'

    def ready(self):
        import social_manager_api.signals
