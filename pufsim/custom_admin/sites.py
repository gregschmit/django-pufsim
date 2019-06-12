from copy import copy
from django.apps import apps
from django.contrib import admin
from django.utils.timezone import get_current_timezone

from pufsim.version import get_version


def tru(*args, **kwargs):
    return True


class SneakyString(str):
    version = f'v{get_version()}'


class CustomAdminSite(admin.AdminSite):
    """
    Provide default branding of the admin portals.
    """
    site_header = SneakyString('pufsim')
    site_version = f'v{get_version()}'
    site_title = f'pufsim {site_version}'
    index_title = 'Home'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        perms = ['module', 'view', 'add', 'change', 'delete']
        other_methods = ['log_addition', 'log_change', 'log_deletion']
        for model,model_admin in admin.site._registry.items():
            if model.__name__ in ['User', 'Group']:
                continue
            new_model_admin = copy(model_admin)
            new_model_admin.admin_site = self
            for p in perms:
                setattr(new_model_admin, f'has_{p}_permission', tru)
            for m in other_methods:
                setattr(new_model_admin, m, tru)
            self._registry[model] = new_model_admin

    def has_permission(self, *args, **kwargs):
        return True

    def smart_sort_models(self, app):
        """
        Sort models in the app models list by ``model_order`` property if it
        exists.
        """
        app_config = apps.get_app_config(app['app_label'])
        models = list(app_config.get_models())
        if all([hasattr(x, 'model_order') for x in models]):
            # inject ordering into dictionary
            for m in models:
                ml = next((x for x in app['models'] if x['object_name'] == m.__name__))
                ml['model_order'] = m.model_order
            app['models'] = sorted(app['models'], key=lambda x: x['model_order'])

    def get_app_list(self, request):
        """
        Sort models by their ``model_order`` property if that property exists
        for all models in the app.
        """
        app_list = super().get_app_list(request)
        for app in app_list:
            self.smart_sort_models(app)
        return app_list

    def app_index(self, *args, **kwargs):
        response = super().app_index(*args, **kwargs)
        # sort response.context_data['app_list'][0]['models']
        self.smart_sort_models(response.context_data['app_list'][0])
        return response


custom_admin_site = CustomAdminSite(name='admin')
