from django.apps import apps
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.Index.as_view()),
    path('test/', views.Test.as_view(), name='test'),
    path('environment/', views.Environment.as_view(), name='environment'),
    path('analysis/', views.Analysis.as_view(), name='analysis'),
    path('bitflip_analyzers/<int:pk>/run/', views.BitflipAnalyzerRun.as_view(), name='run_bitflip_analyzer'),
    path('challenge_pair_analyzers/<int:pk>/run/', views.ChallengePairAnalyzerRun.as_view(), name='run_challenge_pair_analyzer'),
    path('neighbor_predictors/<int:pk>/run/', views.NeighborPredictorRun.as_view(), name='run_neighbor_predictor'),
    path('puf_generators/<int:pk>/quicktest/', views.PUFGeneratorQuicktest.as_view(), name='quicktest_pufg'),
]

# CRUD helper
for m in apps.get_app_config('pufsim').get_models():
    u = m.get_uri_name()
    n = m.__name__
    urlpatterns.append(path(u + '/create/', getattr(views, n + 'Create').as_view(), name='create_' + u))
    urlpatterns.append(path(u + '/<int:pk>/update/', getattr(views, n + 'Update').as_view(), name='update_' + u))
    urlpatterns.append(path(u + '/<int:pk>/delete/', getattr(views, n + 'Delete').as_view(), name='delete_' + u))
    urlpatterns.append(path(u + '/<int:pk>/show/', getattr(views, n + 'Show').as_view(), name='show_' + u))
