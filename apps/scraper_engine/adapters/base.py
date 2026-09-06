from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date, time
from decimal import Decimal
from typing import Optional

@dataclass
class FareResult:
    flight_number: str
    departure_time: Optional[time]
    arrival_time: Optional[time]
    base_fare: Decimal
    taxes_fees: Decimal
    total_fare: Decimal
    seats_available: Optional[int]
    fare_class: str = "economy"
    airline_code: Optional[str] = None   # NEW: needed for multi-airline sources like Yatra

class BaseAirlineAdapter(ABC):
    airline_code: str = None

    @abstractmethod
    def fetch_fares(self, origin: str, destination: str, travel_date: date) -> list[FareResult]:
        raise NotImplementedError