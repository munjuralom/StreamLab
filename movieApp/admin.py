from django.contrib import admin
from .models import Genre, Film

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(Film)
class FilmAdmin(admin.ModelAdmin):
    list_display = (
        "title", "filmmaker", "year", "type", "status",
        "duration_s", "rent_price", "buy_price", "created_at", "views"
    )
    list_filter = ("status", "type", "genre", "currency", "year", "created_at")
    search_fields = ("title", "filmmaker__username", "logline")
    filter_horizontal = ("genre",)
    readonly_fields = ("created_at", "updated_at", "views", "total_earning")

    fieldsets = (
        ("Basic Info", {
            "fields": ("filmmaker", "title", "year", "logline", "type", "genre", "status")
        }),
        ("Media", {
            "fields": ("thumbnail", "trailer", "full_film")
        }),
        ("Pricing & Duration", {
            "fields": ("duration_s", "currency", "rent_price", "rental_hours", "buy_price")
        }),
        ("Stats & Dates", {
            "fields": ("created_at", "updated_at", "published_at", "views", "total_earning")
        }),
    )
