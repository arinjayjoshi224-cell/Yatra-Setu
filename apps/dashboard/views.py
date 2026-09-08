import json
from datetime import date, timedelta
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from apps.catalog.models import Airline, Airport, Route
from apps.pricing.models import PriceSnapshot
from apps.scraper_engine.tasks import scrape_yatra_route
from . import process_manager


def control_panel(request):
    airlines = Airline.objects.all()
    routes = Route.objects.select_related("origin", "destination").all()

    snapshots = PriceSnapshot.objects.select_related("airline", "route__origin", "route__destination").order_by("-scraped_at")

    airline_filter = request.GET.get("airline")
    origin_filter = request.GET.get("origin")
    destination_filter = request.GET.get("destination")

    if airline_filter:
        snapshots = snapshots.filter(airline__code=airline_filter)
    if origin_filter:
        snapshots = snapshots.filter(route__origin__iata_code=origin_filter.upper())
    if destination_filter:
        snapshots = snapshots.filter(route__destination__iata_code=destination_filter.upper())

    snapshots = snapshots[:100]

    return render(request, "dashboard/control_panel.html", {
        "airlines": airlines,
        "routes": routes,
        "snapshots": snapshots,
    })


@csrf_exempt
@require_POST
def start_system(request):
    result = process_manager.start_everything()
    return JsonResponse(result)


@csrf_exempt
@require_POST
def stop_system(request):
    result = process_manager.stop_everything()
    return JsonResponse(result)


@csrf_exempt
@require_POST
def add_route(request):
    data = json.loads(request.body)
    origin, _ = Airport.objects.get_or_create(
        iata_code=data["origin_code"].upper(),
        defaults={"city": data.get("origin_city", ""), "name": data.get("origin_name", "")},
    )
    destination, _ = Airport.objects.get_or_create(
        iata_code=data["destination_code"].upper(),
        defaults={"city": data.get("destination_city", ""), "name": data.get("destination_name", "")},
    )
    route, created = Route.objects.get_or_create(origin=origin, destination=destination)

    # Queue an initial test scrape 7 days out
    target_date = (date.today() + timedelta(days=7)).isoformat()
    scrape_yatra_route.delay(route.id, target_date)

    return JsonResponse({"ok": True, "message": f"Route {origin.iata_code} → {destination.iata_code} added and queued for scraping.", "created": created})


@csrf_exempt
@require_POST
def add_airline(request):
    data = json.loads(request.body)
    airline, created = Airline.objects.get_or_create(
        code=data["code"].upper(),
        defaults={"name": data.get("name", data["code"]), "scraper_adapter_key": "yatra"},
    )
    return JsonResponse({"ok": True, "created": created})
