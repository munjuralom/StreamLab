from django.contrib import admin
from .models import Movie

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'year', 'genre', 'duration',
        'rent_price', 'buy_price',
        'created_by_user', 'clicks', 'created_at'
    )
    list_filter = ('genre', 'year', 'created_at')
    search_fields = ('title', 'logline', 'created_by_user__username')
    readonly_fields = ('clicks', 'created_at', 'updated_at')
    ordering = ('-created_at',)

    fieldsets = (
        ("Movie Info", {
            'fields': (
                'title', 'year', 'logline', 'genre', 'duration'
            )
        }),
        ("Media", {
            'fields': (
                'thumbnail', 'trailer', 'full_film'
            )
        }),
        ("Pricing", {
            'fields': (
                'rent_price', 'buy_price',
            )
        }),
        ("Meta", {
            'fields': (
                'created_by_user', 'clicks', 'created_at', 'updated_at'
            )
        }),
    )
