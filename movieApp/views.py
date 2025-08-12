from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import Film
from .serializers import FilmSerializer

class FilmUploadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = FilmSerializer(data=request.data, context={'request': request})  # Pass context here
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FilmListView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request):
        films = Film.objects.all()
        serializer = FilmSerializer(films, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        return FilmUploadView.as_view()(request)
    
class FilmDetailView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, pk):
        try:
            film = Film.objects.get(pk=pk)
            serializer = FilmSerializer(film)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Film.DoesNotExist:
            return Response({"detail": "Film not found"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        try:
            film = Film.objects.get(pk=pk)
            serializer = FilmSerializer(film, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Film.DoesNotExist:
            return Response({"detail": "Film not found"}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        try:
            film = Film.objects.get(pk=pk)
            film.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Film.DoesNotExist:
            return Response({"detail": "Film not found"}, status=status.HTTP_404_NOT_FOUND)
