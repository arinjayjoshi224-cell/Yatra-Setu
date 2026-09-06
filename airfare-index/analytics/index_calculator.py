import math
from collections import defaultdict
from datetime import datetime
from database.connection import SessionLocal, FlightPriceDB, CalculatedIndexDB

def run_index_pipeline():
    session = SessionLocal()
    try:
        print("Extracting raw fares from PostgreSQL...")
        records = session.query(FlightPriceDB).order_by(FlightPriceDB.scraped_at.asc()).all()
        
        if not records:
            print("Database is empty. Scrape some routes first.")
            return

        print(f"Analyzing {len(records)} price observations...")

        # 1. Determine base price (p0) for each unique matched flight item
        # Item identity: Route + Airline + Flight Number + Departure Time
        base_fares = {}
        for r in records:
            item_key = f"{r.origin}-{r.destination}_{r.airline}_{r.flight_number}_{r.departure_time}"
            if item_key not in base_fares:
                base_fares[item_key] = {
                    "base_fare": r.fare_inr,
                    "base_period": r.scraped_at
                }

        # 2. Group records into batches by route and scrape hour
        batches = defaultdict(list)
        for r in records:
            route = f"{r.origin}-{r.destination}"
            batch_time = r.scraped_at.replace(minute=0, second=0, microsecond=0)
            item_key = f"{r.origin}-{r.destination}_{r.airline}_{r.flight_number}_{r.departure_time}"
            
            p0 = base_fares[item_key]["base_fare"]
            pt = r.fare_inr
            ratio = pt / p0
            
            batches[(route, batch_time)].append({
                "ratio": ratio,
                "base_period": base_fares[item_key]["base_period"]
            })

        # 3. Calculate Jevons Index: exp( (1/n) * sum( ln(pt / p0) ) ) * 100
        index_records = []
        print("\n--- CALCULATED AIRFARE JEVONS INDEX (Base = 100.0) ---")
        print(f"{'Route':<10} | {'Calculation Time':<20} | {'Matched Flights':<15} | {'Jevons Index':<12}")
        print("-" * 65)

        for (route, batch_time), items in batches.items():
            n = len(items)
            log_sum = sum(math.log(item["ratio"]) for item in items)
            jevons_val = round(math.exp(log_sum / n) * 100.0, 2)
            earliest_base = min(item["base_period"] for item in items)

            print(f"{route:<10} | {str(batch_time):<20} | {n:<15} | {jevons_val:<12}")

            index_records.append(
                CalculatedIndexDB(
                    route=route,
                    calculation_time=batch_time,
                    time_horizon="T+30",
                    index_type="JEVONS",
                    index_value=jevons_val,
                    matched_flight_count=n,
                    base_period=earliest_base
                )
            )

        # 4. Save directly to PostgreSQL
        session.bulk_save_objects(index_records)
        session.commit()
        print(f"\nSuccessfully stored {len(index_records)} index calculation(s) into 'airfare_price_indices'.")

    except Exception as e:
        session.rollback()
        print(f"Error computing/saving index: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    run_index_pipeline()