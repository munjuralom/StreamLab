# from rest_framework.views import APIView
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.response import Response
# from rest_framework import status
# from .serializers import FilmSerializer

# class FilmUploadView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request):

#         # title = request.data.get('title')
#         # year = request.data.get('year')
#         # logline = request.data.get('logline')
#         # type = request.data.get('type')
#         # genre = request.data.get('genre')
#         # duration_s = request.data.get('duration_s')
#         # rent_price = request.data.get('rent_price')
#         # buy_price = request.data.get('buy_price')
#         # thumbnail = request.FILES.get('thumbnail')
#         # return Response(thumbnail)
#         serializer = FilmSerializer(data=request.data)
#         if serializer.is_valid():
#             # Pass filmmaker here (assign request.user)
#             film = serializer.save(filmmaker=request.user)
#             return Response(FilmSerializer(film).data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .serializers import FilmSerializer

class FilmUploadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Debug print (optional)
        print("DATA:", request.data)
        print("FILES:", request.FILES)

        serializer = FilmSerializer(data=request.data)
        if serializer.is_valid():
            film = serializer.save(filmmaker=request.user)
            return Response(FilmSerializer(film).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

