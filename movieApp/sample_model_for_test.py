from django.db import models
from django.conf import settings

class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Movie(models.Model):
    title = models.CharField(max_length=255)
    year = models.IntegerField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    genre = models.ForeignKey(Genre, on_delete=models.SET_NULL, null=True, related_name='movies')
    duration = models.IntegerField(help_text='Duration in minutes', blank=True, null=True)
    thumbnail_url = models.URLField(max_length=255, blank=True, null=True)
    trailer_url = models.URLField(max_length=255, blank=True, null=True)
    full_film_url = models.URLField(max_length=255, blank=True, null=True)
    average_rating = models.FloatField(default=0)
    created_by_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_movies')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    categories = models.ManyToManyField(Category, through='MovieCategory', related_name='movies')

    def __str__(self):
        return self.title


class MovieCategory(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('movie', 'category')

    def __str__(self):
        return f"{self.movie.title} - {self.category.name}"


class Rating(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ratings')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='ratings')
    rating = models.PositiveSmallIntegerField()  # We'll validate range separately
    review = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        from django.core.exceptions import ValidationError
        if not (1 <= self.rating <= 5):
            raise ValidationError('Rating must be between 1 and 5.')

    def __str__(self):
        return f"{self.user} rated {self.movie} as {self.rating}"


class Pricing(models.Model):
    movie = models.OneToOneField(Movie, on_delete=models.CASCADE, related_name='pricing')
    rent_price = models.DecimalField(max_digits=6, decimal_places=2)
    buy_price = models.DecimalField(max_digits=6, decimal_places=2)
    currency = models.CharField(max_length=10, default='USD')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Pricing for {self.movie.title}"


class WatchHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='watch_history')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='watch_histories')
    watched_at = models.DateTimeField(auto_now_add=True)
    watch_duration = models.IntegerField(help_text='Watch duration in seconds or minutes', blank=True, null=True)

    def __str__(self):
        return f"{self.user} watched {self.movie} at {self.watched_at}"
