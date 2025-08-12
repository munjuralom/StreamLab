# urls.py
from django.urls import path
from .views import FilmUploadAPIView

urlpatterns = [
    path('upload/', FilmUploadAPIView.as_view(), name='film-upload'),
]
