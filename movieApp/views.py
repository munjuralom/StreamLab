# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from rest_framework.permissions import IsAuthenticated
# from .serializers import FilmSerializer

# class FilmUploadAPIView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request, *args, **kwargs):
#         data = request.data.copy()
#         data['filmmaker'] = request.user.id  # Set logged-in user as filmmaker

#         # return Response(data)
#         serializer = FilmSerializer(data=data)
#         if serializer.is_valid():
#             film = serializer.save()
#             return Response(FilmSerializer(film).data, status=status.HTTP_201_CREATED)
#         else:
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import FilmSerializer

class FilmUploadAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data.copy()
        data['filmmaker'] = request.user.id

        serializer = FilmSerializer(data=data)
        if serializer.is_valid():
            film = serializer.save()
            return Response(FilmSerializer(film).data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

