from rest_framework import serializers
from django.utils import timezone
from .models import Film, Genre

class GenreRelatedField(serializers.RelatedField):
    def to_internal_value(self, data):
        try:
            genre = Genre.objects.get(name__iexact=data)
            return genre
        except Genre.DoesNotExist:
            raise serializers.ValidationError(f"Genre '{data}' does not exist")

    def to_representation(self, value):
        return value.name

class FilmSerializer(serializers.ModelSerializer):
    genre = GenreRelatedField(many=True, queryset=Genre.objects.all(), required=False)
    filmmaker = serializers.PrimaryKeyRelatedField(read_only=True)  # Set in view, not from client

    class Meta:
        model = Film
        fields = [
            "id", "filmmaker", "title", "year", "logline", "type", "genre",
            "thumbnail", "trailer", "full_film",
            "status", "duration_s", "currency",
            "rent_price", "rental_hours", "buy_price",
            "created_at", "updated_at", "published_at",
            "views", "total_earning",
        ]
        read_only_fields = (
            "id", "filmmaker", "created_at", "updated_at",
            "published_at", "views", "total_earning",
        )

    def validate(self, attrs):
        rent_price = attrs.get("rent_price", 0)
        buy_price = attrs.get("buy_price", 0)
        year = attrs.get("year")

        if rent_price < 0 or buy_price < 0:
            raise serializers.ValidationError("Price cannot be negative.")
        if year and (year < 1888 or year > timezone.now().year + 1):
            raise serializers.ValidationError("Invalid year for film.")
        return attrs

    def create(self, validated_data):
        genres = validated_data.pop("genre", [])
        film = Film.objects.create(**validated_data)
        film.genre.set(genres)
        return film

    def update(self, instance, validated_data):
        genres = validated_data.pop("genre", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if genres is not None:
            instance.genre.set(genres)
        return instance
