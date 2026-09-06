from celery import shared_task
from datetime import date, timedelta

from apps.catalog.models import Airline, Route
from apps.pricing.models import ScrapeJob, PriceSnapshot
from .adapters.yatra import YatraAdapter


@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def scrape_yatra_route(self, route_id, travel_date_iso):
    route = Route.objects.get(id=route_id)
    travel_date = date.fromisoformat(travel_date_iso)

    job = ScrapeJob.objects.create(
        airline=Airline.objects.get_or_create(
            code="YATRA", defaults={"name": "Yatra (aggregator)", "scraper_adapter_key": "yatra"}
        )[0],
        route=route, travel_date=travel_date, status="running",
    )
    try:
        adapter = YatraAdapter()
        results = adapter.fetch_fares(route.origin.iata_code, route.destination.iata_code, travel_date)
        for r in results:
            airline, _ = Airline.objects.get_or_create(
                code=r.airline_code, defaults={"name": r.airline_code, "scraper_adapter_key": "yatra"}
            )
            PriceSnapshot.objects.create(
                job=job, airline=airline, route=route, flight_number=r.flight_number,
                travel_date=travel_date, departure_time=r.departure_time, arrival_time=r.arrival_time,
                fare_class=r.fare_class, base_fare=r.base_fare, taxes_fees=r.taxes_fees,
                total_fare=r.total_fare, seats_available=r.seats_available, source_url="yatra.com",
            )
        job.status = "success"
    except Exception as exc:
        job.status = "failed"
        job.error_message = str(exc)
        job.save()
        raise self.retry(exc=exc)
    finally:
        job.save()


@shared_task
def dispatch_yatra_near_term():
    """Daily: refresh the next 7 days, where prices move the most."""
    today = date.today()
    for route in Route.objects.all():
        for day_offset in range(1, 8):
            target_date = today + timedelta(days=day_offset)
            scrape_yatra_route.delay(route.id, target_date.isoformat())


@shared_task
def dispatch_yatra_far_term():
    """Weekly: refresh days 8-30, which are more stable this far out."""
    today = date.today()
    for route in Route.objects.all():
        for day_offset in range(8, 31):
            target_date = today + timedelta(days=day_offset)
            scrape_yatra_route.delay(route.id, target_date.isoformat())