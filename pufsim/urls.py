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
    path('pufgs/<int:pk>/quicktest/', views.PUFGeneratorQuicktest.as_view(), name='quicktest_pufg'),
]

# CRUD helper
cruds = [
    ['pdfs', 'PDF'],
    ['pufgs', 'PUFGenerator'],
    ['bitflip_analyzers', 'BitflipAnalyzer'],
    ['challenge_pair_analyzers', 'ChallengePairAnalyzer'],
]
for c in cruds:
    urlpatterns.append(path(c[0] + '/create/', getattr(views, c[1] + 'Create').as_view(), name='create_' + c[0][:-1]))
    urlpatterns.append(path(c[0] + '/<int:pk>/update/', getattr(views, c[1] + 'Update').as_view(), name='update_' + c[0][:-1]))
    urlpatterns.append(path(c[0] + '/<int:pk>/delete/', getattr(views, c[1] + 'Delete').as_view(), name='delete_' + c[0][:-1]))
    urlpatterns.append(path(c[0] + '/<int:pk>/show/', getattr(views, c[1] + 'Show').as_view(), name='show_' + c[0][:-1]))
