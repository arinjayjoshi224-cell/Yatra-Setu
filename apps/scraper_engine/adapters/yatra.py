import asyncio
import re
from datetime import date, datetime, time as dtime
from decimal import Decimal
from playwright.async_api import async_playwright

from .base import BaseAirlineAdapter, FareResult

# Maps the airline names his scraper reads off the page to your Airline.code values
AIRLINE_NAME_TO_CODE = {
    "IndiGo": "6E",
    "Air India": "AI",
    "SpiceJet": "SG",
    "Akasa Air": "QP",
    "Vistara": "UK",
    "AIX Connect": "IX",
}

def _parse_time(value: str):
    try:
        return datetime.strptime(value, "%H:%M").time()
    except (ValueError, TypeError):
        return None

class YatraAdapter(BaseAirlineAdapter):
    """Aggregator adapter — one call returns fares across multiple airlines."""
    airline_code = "YATRA"  # source identifier, not a real airline

    def fetch_fares(self, origin: str, destination: str, travel_date: date) -> list[FareResult]:
        depart_str = travel_date.strftime("%d/%m/%Y")
        return asyncio.run(self._scrape(origin, destination, depart_str))

    async def _scrape(self, origin: str, dest: str, depart_date: str) -> list[FareResult]:
        search_url = (
            f"https://flight.yatra.com/air-search-ui/dom2/trigger?"
            f"type=O&viewName=normal&flexi=0&noOfSegments=1&"
            f"origin={origin}&originCountry=IN&"
            f"destination={dest}&destinationCountry=IN&"
            f"flight_depart_date={depart_date}&"
            f"ADT=1&CHD=0&INF=0&class=Economy&source=fresco-home"
        )

        results: list[FareResult] = []

        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=False,  # must be headless for Celery/server use
                args=[
                    "--disable-http2",
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                ],
            )
            context = await browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
                ),
                viewport={"width": 1400, "height": 900},
            )
            page = await context.new_page()

            try:
                await page.goto("https://www.yatra.com", timeout=20000, wait_until="domcontentloaded")
                await page.wait_for_timeout(1500)
            except Exception:
                pass

            await page.goto(search_url, timeout=60000, wait_until="domcontentloaded")

            card_selector = "div.flight-item"
            try:
                await page.wait_for_selector(card_selector, timeout=30000)
            except Exception:
                card_selector = "div.tuple"
                await page.wait_for_selector(card_selector, timeout=10000)

            await page.wait_for_timeout(3500)
            cards = await page.query_selector_all(card_selector)

            for card in cards:
                text = await card.inner_text()
                lines = [line.strip() for line in text.split("\n") if line.strip()]

                fare_inr = None
                for idx, line in enumerate(lines):
                    if any(btn in line for btn in ["View Fares", "Book Now", "Book"]):
                        for prev_line in reversed(lines[:idx]):
                            clean = re.sub(r"[^\d]", "", prev_line)
                            if clean.isdigit() and int(clean) >= 1500:
                                fare_inr = int(clean)
                                break
                        if fare_inr:
                            break

                if not fare_inr:
                    matches = re.findall(r"(?:₹\s*|Rs\.?\s*)?([1-9]\d{0,2},\d{3})", text)
                    non_promos = [m for m in matches if m not in ["3,000", "5,000", "4,500"]]
                    if non_promos:
                        fare_inr = int(non_promos[-1].replace(",", ""))

                airline_name = "Unknown"
                flight_num = ""
                for line in lines:
                    if any(al in line for al in AIRLINE_NAME_TO_CODE):
                        airline_name = line
                    elif re.search(r"^(6E|AI|SG|QP|UK|I5|IX)[-\s]?\d+", line):
                        flight_num = line

                times = re.findall(r"\b([0-2]?\d:[0-5]\d)\b", text)
                dep_time = times[0] if len(times) > 0 else None
                arr_time = times[1] if len(times) > 1 else None

                airline_code = AIRLINE_NAME_TO_CODE.get(airline_name)
                if fare_inr and airline_code:
                    results.append(
                        FareResult(
                            flight_number=flight_num,
                            departure_time=_parse_time(dep_time),
                            arrival_time=_parse_time(arr_time),
                            base_fare=Decimal(fare_inr),
                            taxes_fees=Decimal(0),
                            total_fare=Decimal(fare_inr),
                            seats_available=None,
                            fare_class="economy",
                            airline_code=airline_code,
                        )
                    )

            await browser.close()

        return results