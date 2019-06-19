from django.urls import path, include
from django.views.generic import RedirectView

from .custom_admin.sites import custom_admin_site
from .views import PUFGeneratorQuicktest


urlpatterns = [
    path('admin/pufsim/pufgenerator/<int:pk>/quicktest', PUFGeneratorQuicktest.as_view(), name='pufgenerator_quicktest'),
    path('admin/', custom_admin_site.urls),
    path('', RedirectView.as_view(url='/admin')),
]
