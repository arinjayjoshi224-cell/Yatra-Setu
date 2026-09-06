import asyncio
import re
from datetime import datetime
from playwright.async_api import async_playwright
from database.connection import FlightPriceDB, SessionLocal, init_db

async def scrape_and_save(origin: str, dest: str, depart_date: str):
    search_url = (
        f"https://flight.yatra.com/air-search-ui/dom2/trigger?"
        f"type=O&viewName=normal&flexi=0&noOfSegments=1&"
        f"origin={origin}&originCountry=IN&"
        f"destination={dest}&destinationCountry=IN&"
        f"flight_depart_date={depart_date}&"
        f"ADT=1&CHD=0&INF=0&class=Economy&source=fresco-home"
    )

    records_to_insert = []

    async with async_playwright() as p:
        # Launch Chromium with HTTP/2 disabled and automation bypass flags
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--disable-http2",
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox"
            ]
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            viewport={"width": 1400, "height": 900}
        )
        page = await context.new_page()

        # Warm up session cookies to prevent connection drops
        print("Initializing session on Yatra...")
        try:
            await page.goto("https://www.yatra.com", timeout=20000, wait_until="domcontentloaded")
            await page.wait_for_timeout(1500)
        except Exception:
            pass

        print(f"Navigating to {origin} -> {dest} for date {depart_date}...")
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

            # Extract fare
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

            # Extract airline and flight number
            airline = "Unknown"
            flight_num = ""
            for line in lines:
                if any(al in line for al in ["IndiGo", "Air India", "SpiceJet", "Akasa Air", "Vistara", "AIX Connect"]):
                    airline = line
                elif re.search(r"^(6E|AI|SG|QP|UK|I5|IX)[-\s]?\d+", line):
                    flight_num = line

            # Extract times
            times = re.findall(r"\b([0-2]?\d:[0-5]\d)\b", text)
            dep_time = times[0] if len(times) > 0 else "--:--"
            arr_time = times[1] if len(times) > 1 else "--:--"

            if fare_inr and airline != "Unknown":
                db_record = FlightPriceDB(
                    source_platform="Yatra",
                    airline=airline,
                    flight_number=flight_num,
                    origin=origin,
                    destination=dest,
                    departure_time=dep_time,
                    arrival_time=arr_time,
                    fare_inr=fare_inr,
                    travel_date=depart_date,
                    scraped_at=datetime.utcnow()
                )
                records_to_insert.append(db_record)

        await browser.close()

    # Commit to PostgreSQL
    if records_to_insert:
        session = SessionLocal()
        try:
            session.bulk_save_objects(records_to_insert)
            session.commit()
            print(f"Successfully inserted {len(records_to_insert)} records into PostgreSQL!")
        except Exception as e:
            session.rollback()
            print(f"Database error: {e}")
        finally:
            session.close()
    else:
        print("No valid records parsed to insert.")

if __name__ == "__main__":
    init_db()
    asyncio.run(scrape_and_save("DEL", "BOM", "06/10/2026"))