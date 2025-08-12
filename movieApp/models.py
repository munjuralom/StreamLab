from django.db import models
from accounts.models import User
from django.utils.translation import gettext_lazy as _
import shortuuid
from cloudinary.models import CloudinaryField

# Helper
def generate_short_uuid() -> str:
    return shortuuid.uuid()[:10]

class FilmStatus(models.TextChoices):
    REVIEW = "review", _("In Review")
    PUBLISHED = "published", _("Published")
    REJECTED = "rejected", _("Rejected")

class FilmType(models.TextChoices):
    MOVIE = "movie", _("Movie")
    DRAMA = "drama", _("Drama")
    SHORT = "short", _("Short")
    DOCUMENTARY = "documentary", _("Documentary")
    SERIES = "series", _("Series")

class Genre(models.Model):
    name = models.CharField(max_length=60, unique=True)

    class Meta:
        verbose_name_plural = "Genres"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Film(models.Model):
    id = models.CharField(
        primary_key=True, max_length=10,
        default=generate_short_uuid, editable=False, unique=True
    )
    filmmaker = models.ForeignKey(User, on_delete=models.CASCADE, related_name="films")
    title = models.CharField(max_length=200)
    year = models.PositiveSmallIntegerField(null=True, blank=True)
    logline = models.CharField(max_length=280, blank=True)
    type = models.CharField(max_length=20, choices=FilmType.choices)
    genre = models.ManyToManyField(Genre, blank=True)

    # Cloudinary uploads (separate folders)
    thumbnail = CloudinaryField('image', folder='thumbnails')
    trailer = CloudinaryField(resource_type='video', folder='trailers')
    full_film = CloudinaryField(resource_type='video', folder='full_films')

    status = models.CharField(max_length=12, choices=FilmStatus.choices, default=FilmStatus.REVIEW)
    duration_s = models.PositiveIntegerField(default=0, help_text="Duration in seconds")
    currency = models.CharField(max_length=3, default="USD")
    rent_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    rental_hours = models.PositiveIntegerField(default=48)
    buy_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)

    views = models.PositiveIntegerField(default=0)
    total_earning = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} ({self.year}) - {self.filmmaker.email}"

# class FilmWatchHistory(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watch_history")
#     film = models.ForeignKey(Film, on_delete=models.CASCADE, related_name="watch_history")
#     watched_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         unique_together = ('user', 'film')
#         ordering = ["-watched_at"]

#     def __str__(self):
#         return f"{self.user.username} watched {self.film.title} on {self.watched_at}"