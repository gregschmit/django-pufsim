from django.apps import AppConfig


class CustomConfig(AppConfig):
    name = 'pufsim.analysis'
    label = 'pufsim_analysis'
    verbose_name = "PUFSim Analysis"

    def ready(self):
        pass # startup code
