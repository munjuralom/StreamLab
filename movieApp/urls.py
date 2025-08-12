# urls.py
from django.urls import path
from .views import FilmUploadView

urlpatterns = [
    path('upload/', FilmUploadView.as_view(), name='film-upload'),
]
