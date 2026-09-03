from django.db import models

class Airline(models.Model):
    code = models.CharField(max_length=3, unique=True)      # "6E", "AI", "SG"
    name = models.CharField(max_length=100)                 # "IndiGo"
    scraper_adapter_key = models.CharField(max_length=50)    # maps to adapter class
    is_active = models.BooleanField(default=True)
    scrape_interval_minutes = models.PositiveIntegerField(default=180)

class Airport(models.Model):
    iata_code = models.CharField(max_length=3, unique=True)  # "DEL", "BOM"
    city = models.CharField(max_length=100)
    name = models.CharField(max_length=150)

class Route(models.Model):
    origin = models.ForeignKey(Airport, related_name="routes_from", on_delete=models.CASCADE)
    destination = models.ForeignKey(Airport, related_name="routes_to", on_delete=models.CASCADE)
    is_domestic = models.BooleanField(default=True)

    class Meta:
        unique_together = ("origin", "destination")
