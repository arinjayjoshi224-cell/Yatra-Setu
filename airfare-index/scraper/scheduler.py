import asyncio
from datetime import datetime, timedelta
from scraper.yatra_scraper import scrape_and_save

# Top domestic corridors by traffic volume (DGCA weights)
ROUTES = [
    ("DEL", "BOM"),
    ("BOM", "DEL"),
    ("BLR", "DEL"),
    ("DEL", "BLR"),
    ("BOM", "BLR"),
]

# Horizons: T+1, T+7, T+15, T+30
LEAD_DAYS = [1, 7, 15, 30]

async def run_full_matrix():
    today = datetime.now()

    for origin, dest in ROUTES:
        for lead in LEAD_DAYS:
            target_date = (today + timedelta(days=lead)).strftime("%d/%m/%Y")
            print(f"\n==========================================")
            print(f"Processing: {origin} -> {dest} | Horizon: T+{lead} ({target_date})")
            print(f"==========================================")
            
            try:
                await scrape_and_save(origin, dest, target_date)
            except Exception as e:
                print(f"Error scraping {origin}->{dest} on {target_date}: {e}")
            
            # Anti-ban sleep jitter between requests
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(run_full_matrix())