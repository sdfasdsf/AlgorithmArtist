from django.apps import AppConfig


class AiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "AI"

    def ready(self):
        from .fetch_movies import start_receive
        start_receive()