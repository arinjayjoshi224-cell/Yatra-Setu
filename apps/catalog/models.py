from django.db import models


class Airline(models.Model):
    code = models.CharField(max_length=3, unique=True)
    name = models.CharField(max_length=100)
    scraper_adapter_key = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    scrape_interval_minutes = models.PositiveIntegerField(default=180)

    def __str__(self):
        return f"{self.name} ({self.code})"


class Airport(models.Model):
    iata_code = models.CharField(max_length=3, unique=True)
    city = models.CharField(max_length=100)
    name = models.CharField(max_length=150)

    def __str__(self):
        return f"{self.iata_code} - {self.city}"


class Route(models.Model):
    origin = models.ForeignKey(Airport, related_name="routes_from", on_delete=models.CASCADE)
    destination = models.ForeignKey(Airport, related_name="routes_to", on_delete=models.CASCADE)
    is_domestic = models.BooleanField(default=True)

    class Meta:
        unique_together = ("origin", "destination")

    def __str__(self):
        return f"{self.origin.iata_code} → {self.destination.iata_code}"