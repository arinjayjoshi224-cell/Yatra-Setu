import json
import os


def save_flight_data(
    flights: list,
    filename: str = "flight_prices.json"
) -> None:

    existing_data = []

    if os.path.exists(filename):
        try:
            with open(filename, "r", encoding="utf-8") as file:
                existing_data = json.load(file)

        except (json.JSONDecodeError, FileNotFoundError):
            existing_data = []

    existing_data.extend(flights)

    with open(filename, "w", encoding="utf-8") as file:
        json.dump(existing_data, file, indent=4)
