from scraper import scrape_flights_from_response
from storage import save_flight_data


def main():

    flights = scrape_flights_from_response(
        response_file="../search_response.json",
        airline="IndiGo",
        origin="DEL",
        destination="CCU",
        travel_date="2026-09-20"
    )

    if flights:
        save_flight_data(flights)
        print(f"{len(flights)} flight records saved successfully.")
    else:
        print("No flight data collected.")


if __name__ == "__main__":
    main()