from django.apps import AppConfig


class CoworkersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "coworkers"

    def ready(self):
        import coworkers.signals
