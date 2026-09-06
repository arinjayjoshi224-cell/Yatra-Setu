from database.connection import SessionLocal, FlightPriceDB

session = SessionLocal()
records = session.query(FlightPriceDB).order_by(FlightPriceDB.id.asc()).all()

print(f"Total Rows: {len(records)}\n")
for r in records:
    print(f"[{r.id}] {r.airline} {r.flight_number} | {r.origin}->{r.destination} | {r.departure_time} | ₹{r.fare_inr} | {r.travel_date} | {r.scraped_at}")

session.close()