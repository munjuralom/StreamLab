from django.db import models
from cloudinary.models import CloudinaryField
from django.contrib.auth import get_user_model

User = get_user_model()

class Movie(models.Model):
    GENRE_CHOICES = [
        ('action', 'Action'),
        ('comedy', 'Comedy'),
        ('drama', 'Drama'),
        ('horror', 'Horror'),
        ('sci-fi', 'Sci-Fi'),
        ('romance', 'Romance'),
        ('documentary', 'Documentary'),
        ('other', 'Other'),
    ]

    title = models.CharField(max_length=255)
    year = models.PositiveIntegerField()
    logline = models.TextField(help_text="Short summary of the movie")
    genre = models.CharField(max_length=50, choices=GENRE_CHOICES)
    duration = models.PositiveIntegerField(help_text="Duration in minutes")

    thumbnail = CloudinaryField('image')  # Movie poster/thumbnail
    trailer = CloudinaryField('video', resource_type="video")  # Short trailer video
    full_film = CloudinaryField('video', resource_type="video")  # Full movie file

    created_by_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='movies')
    rent_price = models.DecimalField(max_digits=10, decimal_places=2)
    buy_price = models.DecimalField(max_digits=10, decimal_places=2)

    clicks = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.year})"
