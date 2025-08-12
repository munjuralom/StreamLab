from django.contrib import admin
from .models import Genre, Film, WatchProgress


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    ordering = ("name",)


class WatchProgressInline(admin.TabularInline):
    model = WatchProgress
    extra = 0
    readonly_fields = ("user", "position_s", "duration_s", "completed", "last_watched_at", "percent_display")

    def percent_display(self, obj):
        return f"{obj.percent}%"
    percent_display.short_description = "Progress"


@admin.register(Film)
class FilmAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "filmmaker",
        "type",
        "display_genres",  # Custom method to show genres as comma-separated
        "status",
        "year",
        "views",
        "rent_price",
        "buy_price",
        "total_earning",
        "created_at",
    )
    list_filter = ("status", "type", "year", "currency", "created_at")
    search_fields = ("title", "filmmaker__full_name", "filmmaker__email", "logline")
    readonly_fields = ("id", "created_at", "updated_at", "published_at", "views", "total_earning")
    inlines = [WatchProgressInline]
    date_hierarchy = "created_at"
    ordering = ("-created_at",)

    fieldsets = (
        ("Basic Info", {
            "fields": ("id", "filmmaker", "title", "year", "logline", "type", "genre", "status")
        }),
        ("Media URLs", {
            "fields": ("thumbnail", "trailer", "full_film")  # If you want to upload in admin
        }),
        ("Pricing", {
            "fields": ("currency", "rent_price", "rental_hours", "buy_price")
        }),
        ("Analytics", {
            "fields": ("views", "total_earning")
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at", "published_at")
        }),
    )

    def display_genres(self, obj):
        return ", ".join(genre.name for genre in obj.genre.all())
    display_genres.short_description = "Genres"


@admin.register(WatchProgress)
class WatchProgressAdmin(admin.ModelAdmin):
    list_display = ("user", "film", "position_s", "duration_s", "percent_display", "completed", "last_watched_at")
    search_fields = ("user__full_name", "user__email", "film__title")
    list_filter = ("completed", "last_watched_at")
    readonly_fields = ("percent_display",)

    def percent_display(self, obj):
        return f"{obj.percent}%"
    percent_display.short_description = "Progress"
