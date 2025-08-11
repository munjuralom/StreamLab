from django.urls import path
from .views import MovieUploadView

urlpatterns = [
    path('upload-movie/', MovieUploadView.as_view(), name='upload-movie'),
]