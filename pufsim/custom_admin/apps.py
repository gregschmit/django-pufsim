from django.apps import AppConfig


class CustomConfig(AppConfig):
    name = 'pufsim.custom_admin'
    label = 'pufsim_admin'
    verbose_name = "PUFSim Admin"

    def ready(self):
        pass # startup code
