from django.db import models

class ScrapeJob(models.Model):
    STATUS = [("pending", "Pending"), ("running", "Running"),
               ("success", "Success"), ("failed", "Failed")]
    airline = models.ForeignKey("catalog.Airline", on_delete=models.CASCADE)
    route = models.ForeignKey("catalog.Route", on_delete=models.CASCADE)
    travel_date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS, default="pending")
    started_at = models.DateTimeField(null=True)
    finished_at = models.DateTimeField(null=True)
    error_message = models.TextField(blank=True)
    retry_count = models.PositiveSmallIntegerField(default=0)

class PriceSnapshot(models.Model):
    """One scrape result — a specific flight, on a specific search, at a point in time."""
    job = models.ForeignKey(ScrapeJob, on_delete=models.CASCADE, related_name="snapshots")
    airline = models.ForeignKey("catalog.Airline", on_delete=models.CASCADE)
    route = models.ForeignKey("catalog.Route", on_delete=models.CASCADE)
    flight_number = models.CharField(max_length=10, blank=True)
    travel_date = models.DateField()
    departure_time = models.TimeField(null=True)
    arrival_time = models.TimeField(null=True)
    fare_class = models.CharField(max_length=20, default="economy")
    base_fare = models.DecimalField(max_digits=10, decimal_places=2)
    taxes_fees = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_fare = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default="INR")
    seats_available = models.PositiveSmallIntegerField(null=True)
    scraped_at = models.DateTimeField(auto_now_add=True)
    source_url = models.URLField(blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["airline", "route", "travel_date"]),
            models.Index(fields=["scraped_at"]),
        ]

class PriceHistory(models.Model):
    """Denormalized daily aggregate for fast trend queries."""
    airline = models.ForeignKey("catalog.Airline", on_delete=models.CASCADE)
    route = models.ForeignKey("catalog.Route", on_delete=models.CASCADE)
    travel_date = models.DateField()
    date_recorded = models.DateField()
    min_fare = models.DecimalField(max_digits=10, decimal_places=2)
    max_fare = models.DecimalField(max_digits=10, decimal_places=2)
    avg_fare = models.DecimalField(max_digits=10, decimal_places=2)
    sample_count = models.PositiveIntegerField()

    class Meta:
        unique_together = ("airline", "route", "travel_date", "date_recorded")
