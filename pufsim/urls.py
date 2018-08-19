from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.Index.as_view()),
    path('environment/', views.Environment.as_view(), name='environment'),
    path('analysis/', views.Analysis.as_view(), name='analysis'),
    #path('pdfs/create/', views.PDFCreate.as_view(), name='create_pdf'),
    #path('pdfs/<int:pk>/update/', views.PDFUpdate.as_view(), name='update_pdf'),
    #path('pdfs/<int:pk>/delete/', views.PDFDelete.as_view(), name='delete_pdf'),
    #path('pufgs/create/', views.PUFGeneratorCreate.as_view(), name='create_pufg'),
    #path('pufgs/<int:pk>/update/', views.PUFGeneratorUpdate.as_view(), name='update_pufg'),
    #path('pufgs/<int:pk>/delete/', views.PUFGeneratorDelete.as_view(), name='delete_pufg'),
    path('pufgs/<int:pk>/quicktest/', views.PUFGeneratorQuicktest.as_view(), name='quicktest_pufg'),
]

# CRUD helper
cuds = [
    ['pdfs', 'PDF'],
    ['pufgs', 'PUFGenerator'],
    ['bitflip_analyzers', 'BitflipAnalyzer'],
]
for c in cuds:
    urlpatterns.append(path(c[0] + '/create/', getattr(views, c[1] + 'Create').as_view(), name='create_' + c[0][:-1]))
    urlpatterns.append(path(c[0] + '/<int:pk>/update/', getattr(views, c[1] + 'Update').as_view(), name='update_' + c[0][:-1]))
    urlpatterns.append(path(c[0] + '/<int:pk>/delete/', getattr(views, c[1] + 'Delete').as_view(), name='delete_' + c[0][:-1]))
