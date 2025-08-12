from rest_framework import serializers
from .models import Film, Genre

class FilmSerializer(serializers.ModelSerializer):
    genre = serializers.ListField(child=serializers.CharField(), write_only=True)
    genres_display = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Film
        fields = '__all__'
        read_only_fields = ('filmmaker',)

    def get_genres_display(self, obj):
        return [g.name for g in obj.genre.all()]

    def create(self, validated_data):
        genre_names = validated_data.pop("genre", [])
        user = self.context['request'].user  # current logged-in user
        film = Film.objects.create(filmmaker=user, **validated_data)

        genre_objs = []
        for name in genre_names:
            genre_obj, _ = Genre.objects.get_or_create(name=name.strip())
            genre_objs.append(genre_obj)
        film.genre.set(genre_objs)
        return film
