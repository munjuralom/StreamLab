from django.db import models
from accounts.models import User
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.exceptions import ValidationError
import shortuuid
from cloudinary.models import CloudinaryField

# ---------- helpers ----------
def generate_short_uuid() -> str:
    """Generate a short UUID for primary keys."""
    return shortuuid.uuid()[:10]

# ---------- choices ----------
class FilmStatus(models.TextChoices):
    REVIEW = "review", _("In Review")       # default
    PUBLISHED = "published", _("Published")
    REJECTED = "rejected", _("Rejected")

class FilmType(models.TextChoices):
    MOVIE = "movie", _("Movie")
    DRAMA = "drama", _("Drama")
    SHORT = "short", _("Short")
    DOCUMENTARY = "documentary", _("Documentary")
    SERIES = "series", _("Series")

# ---------- core ----------
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
    genre = models.ManyToManyField(Genre, blank=True)  # Changed to ManyToManyField

    # Cloudinary uploads (separate folders)
    # thumbnail = models.FileField(upload_to="thumbnail/", blank=True, null=True)
    # trailer = models.FileField(upload_to="trailer/", blank=True, null=True)
    # full_film = models.FileField(upload_to="full_film/", blank=True, null=True)
    
    # Cloudinary uploads (separate folders)
    thumbnail = CloudinaryField('thumbnail', blank=True, null=True)
    trailer = CloudinaryField('trailer', blank=True, null=True)
    full_film = CloudinaryField('full_film', blank=True, null=True)

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
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["type"]),
            # ManyToManyFields are not indexed like this; you can add indexes on Genre model if needed
        ]

    def __str__(self):
        return self.title

    def clean(self):
        """Custom validations."""
        if self.rent_price < 0 or self.buy_price < 0:
            raise ValidationError(_("Price cannot be negative."))
        if self.year and (self.year < 1888 or self.year > timezone.now().year + 1):
            raise ValidationError(_("Invalid year for film."))

    def publish(self):
        """Publish film and set publish date."""
        self.status = FilmStatus.PUBLISHED
        self.published_at = timezone.now()
        self.save(update_fields=["status", "published_at"])


# ---------- Watch Progress ----------
class WatchProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watch_progress")
    film = models.ForeignKey(Film, on_delete=models.CASCADE, related_name="watch_progress")
    position_s = models.PositiveIntegerField(default=0)
    duration_s = models.PositiveIntegerField(default=0)
    completed = models.BooleanField(default=False)
    last_watched_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (("user", "film"),)
        indexes = [models.Index(fields=["user", "film"])]

    @property
    def percent(self) -> int:
        if not self.duration_s:
            return 0
        p = int((self.position_s / max(1, self.duration_s)) * 100)
        return 100 if self.completed else min(p, 99)

    def __str__(self):
        return f"{self.user} - {self.film} ({self.percent}%)"
