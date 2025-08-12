from rest_framework import serializers
from .models import Film, Genre

class FilmSerializer(serializers.ModelSerializer):
    genre = serializers.CharField(write_only=True)

    class Meta:
        model = Film
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'published_at', 'views', 'total_earning')

    def validate_genre(self, value):
        genre_names = [name.strip() for name in value.split(',') if name.strip()]
        if not genre_names:
            return []

        genres = Genre.objects.filter(name__in=genre_names)
        found_names = set(g.name for g in genres)
        missing = set(genre_names) - found_names
        if missing:
            raise serializers.ValidationError(f"Genres not found: {', '.join(missing)}")

        return genres

    def create(self, validated_data):
        genres = validated_data.pop('genre', [])
        film = Film.objects.create(**validated_data)
        film.genre.set(genres)
        return film
