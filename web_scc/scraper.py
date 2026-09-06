from datetime import datetime
import json


def scrape_flights_from_response(
    response_file: str,
    airline: str,
    origin: str,
    destination: str,
    travel_date: str
) -> list:

    with open(response_file, "r", encoding="utf-8") as file:
        data = json.load(file)

    flights = []

    trips = data.get("data", {}).get("trips", [])

    for trip in trips:

        journeys = trip.get("journeysAvailable", [])

        for journey in journeys:

            designator = journey.get("designator", {})

            flight_origin = designator.get("origin")
            flight_destination = designator.get("destination")

            # Keep only the requested route.
            if (
                flight_origin != origin
                or flight_destination != destination
            ):
                continue

            segments = journey.get("segments", [])

            if not segments:
                continue

            if journey.get("flightType") != "NonStop":
                continue

            segment = segments[0]

            identifier = segment.get("identifier", {})

            flight_number = identifier.get("identifier")

            departure = designator.get("departure")
            arrival = designator.get("arrival")

            duration = calculate_duration(
                departure,
                arrival
            )

            price = find_lowest_economy_fare(journey)

            if price is None:
                continue

            flight_record = {
                "airline": airline,
                "flight_number": flight_number,
                "origin": flight_origin,
                "destination": flight_destination,
                "travel_date": travel_date,
                "departure": departure,
                "arrival": arrival,
                "duration": duration,
                "price": price,
                "currency": "INR",
                "checked_at": datetime.now().isoformat()
            }

            flights.append(flight_record)

    return flights


def find_lowest_economy_fare(journey):

    fares = journey.get("passengerFares", [])

    economy_prices = []

    for fare in fares:

        if fare.get("FareClass") != "Economy":
            continue

        if not fare.get("isActive", False):
            continue

        total_fare = fare.get("totalFareAmount")

        if total_fare is not None:
            economy_prices.append(float(total_fare))

    if not economy_prices:
        return None

    return min(economy_prices)


def calculate_duration(departure, arrival):

    if not departure or not arrival:
        return ""

    departure_time = datetime.fromisoformat(departure)
    arrival_time = datetime.fromisoformat(arrival)

    difference = arrival_time - departure_time

    total_minutes = int(
        difference.total_seconds() / 60
    )

    hours = total_minutes // 60
    minutes = total_minutes % 60

    return f"{hours}h {minutes}m"


if __name__ == "__main__":

    flights = scrape_flights_from_response(
        response_file="../search_response.json",
        airline="IndiGo",
        origin="DEL",
        destination="CCU",
        travel_date="2026-09-20"
    )

    print()

    for flight in flights:
        print(flight)