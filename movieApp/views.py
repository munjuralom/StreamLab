from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .serializers import MovieSerializer

class MovieUploadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        data = request.data.copy()
        data['created_by_user'] = request.user.id
        serializer = MovieSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Movie uploaded successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
