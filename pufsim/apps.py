from django.apps import AppConfig


class CustomConfig(AppConfig):
    name = 'pufsim'
    verbose_name = "PUFSim"

    def ready(self):
        pass # startup code
