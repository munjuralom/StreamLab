from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
import cloudinary.uploader
import boto3
from django.conf import settings
from .models import Film
from .serializers import FilmSerializer  # assume you made one for Film

class FilmUploadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        data = request.data.copy()
        data['filmmaker'] = request.user.id

        # Upload thumbnail to Cloudinary
        thumbnail_file = request.FILES.get('thumbnail')
        if thumbnail_file:
            upload_result = cloudinary.uploader.upload(thumbnail_file, folder="films/thumbnails", resource_type="image")
            data['thumbnail_url'] = upload_result.get('secure_url')

        # Upload trailer to Cloudinary (video)
        trailer_file = request.FILES.get('trailer')
        if trailer_file:
            upload_result = cloudinary.uploader.upload(trailer_file, folder="films/trailers", resource_type="video")
            data['trailer_url'] = upload_result.get('secure_url')

        # Upload full film to S3 (big file)
        full_film_file = request.FILES.get('full_film')
        if full_film_file:
            s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_S3_REGION_NAME
            )
            key = f'full_films/{full_film_file.name}'
            s3_client.upload_fileobj(
                full_film_file,
                settings.AWS_STORAGE_BUCKET_NAME,
                key,
                ExtraArgs={'ACL': 'public-read', 'ContentType': full_film_file.content_type}
            )
            s3_url = f'https://{settings.AWS_S3_CUSTOM_DOMAIN}/{key}'
            data['full_film_url'] = s3_url

        serializer = FilmSerializer(data=data)
        if serializer.is_valid():
            film = serializer.save()
            return Response({"message": "Film uploaded successfully", "data": FilmSerializer(film).data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
