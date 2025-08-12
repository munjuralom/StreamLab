from django.urls import path
from .views import FilmUploadView, FilmListView, FilmDetailView
urlpatterns = [
    path('films-list/', FilmListView.as_view(), name='film-list'),
    path('films/<str:pk>/', FilmDetailView.as_view(), name='film-detail'),
    path('upload/', FilmUploadView.as_view(), name='film-upload'),
]