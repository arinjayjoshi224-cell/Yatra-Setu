import asyncio
import re
from playwright.async_api import async_playwright

async def scrape_yatra_flights(origin: str, dest: str, depart_date: str):
    url = (
        f"https://flight.yatra.com/air-search-ui/dom2/trigger?"
        f"type=O&viewName=normal&flexi=0&noOfSegments=1&"
        f"origin={origin}&originCountry=IN&"
        f"destination={dest}&destinationCountry=IN&"
        f"flight_depart_date={depart_date}&"
        f"ADT=1&CHD=0&INF=0&class=Economy&source=fresco-home"
    )

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            viewport={"width": 1400, "height": 900}
        )
        page = await context.new_page()

        print(f"Navigating to {origin} -> {dest} for {depart_date}...")
        await page.goto(url, wait_until="domcontentloaded")

        card_selector = "div.flight-item"
        try:
            await page.wait_for_selector(card_selector, timeout=30000)
        except Exception:
            card_selector = "div.tuple"
            await page.wait_for_selector(card_selector, timeout=10000)

        # Allow rendered fares to settle
        await page.wait_for_timeout(3500)

        cards = await page.query_selector_all(card_selector)
        print(f"Found {len(cards)} flights. Parsing:\n")

        valid_flights = []

        for card in cards:
            text = await card.inner_text()
            lines = [line.strip() for line in text.split("\n") if line.strip()]

            # 1. Extract Fare: find line immediately before 'View Fares' or 'Book'
            fare_inr = None
            for idx, line in enumerate(lines):
                if any(btn in line for btn in ["View Fares", "Book Now", "Book"]):
                    # Step backwards to find the nearest price string
                    for prev_line in reversed(lines[:idx]):
                        clean = re.sub(r"[^\d]", "", prev_line)
                        if clean.isdigit() and int(clean) >= 1500:
                            fare_inr = int(clean)
                            break
                    if fare_inr:
                        break

            # Fallback regex if layout shifts
            if not fare_inr:
                matches = re.findall(r"(?:₹\s*|Rs\.?\s*)?([1-9]\d{0,2},\d{3})", text)
                # Filter out promo amounts (3,000 / 5,000)
                non_promos = [m for m in matches if m not in ["3,000", "5,000", "4,500"]]
                if non_promos:
                    fare_inr = int(non_promos[-1].replace(",", ""))

            # 2. Extract Airline & Flight Code
            airline = "Unknown"
            flight_num = ""
            for line in lines:
                if any(al in line for al in ["IndiGo", "Air India", "SpiceJet", "Akasa Air", "Vistara", "AIX Connect"]):
                    airline = line
                elif re.search(r"^(6E|AI|SG|QP|UK|I5|IX)[-\s]?\d+", line):
                    flight_num = line

            # 3. Extract Times (matches HH:MM pattern)
            times = re.findall(r"\b([0-2]?\d:[0-5]\d)\b", text)
            dep_time = times[0] if len(times) > 0 else "--:--"
            arr_time = times[1] if len(times) > 1 else "--:--"

            if fare_inr and airline != "Unknown":
                flight_data = {
                    "airline": airline,
                    "flight_number": flight_num,
                    "dep_time": dep_time,
                    "arr_time": arr_time,
                    "fare_inr": fare_inr,
                    "route": f"{origin}->{dest}",
                    "date": depart_date
                }
                valid_flights.append(flight_data)
                print(f"✈️  {airline:<12} {flight_num:<14} | {dep_time} -> {arr_time} | ₹{fare_inr}")

        print(f"\nSuccessfully extracted {len(valid_flights)} structured flight records.")
        await browser.close()
        return valid_flights

if __name__ == "__main__":
    asyncio.run(scrape_yatra_flights("DEL", "BOM", "06/10/2026"))