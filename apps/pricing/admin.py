from django.contrib import admin
from .models import ScrapeJob, PriceSnapshot, PriceHistory


@admin.register(PriceSnapshot)
class PriceSnapshotAdmin(admin.ModelAdmin):
    list_display = ("airline", "route", "travel_date", "total_fare", "scraped_at")
    list_filter = ("airline",)
    ordering = ("-scraped_at",)
    readonly_fields = ("scraped_at",)   # NEW: makes it visible (but not editable) on the detail page


@admin.register(ScrapeJob)
class ScrapeJobAdmin(admin.ModelAdmin):
    list_display = ("airline", "route", "travel_date", "status", "finished_at")
    list_filter = ("status", "airline")


admin.site.register(PriceHistory)