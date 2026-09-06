from database.connection import SessionLocal, FlightPriceDB

session = SessionLocal()
count = session.query(FlightPriceDB).count()
print(f"Total flights in DB: {count}")

latest_records = session.query(FlightPriceDB).order_by(FlightPriceDB.id.desc()).limit(5).all()
for r in latest_records:
    print(f"[{r.id}] {r.airline} {r.flight_number} | {r.origin}->{r.destination} | {r.departure_time} | ₹{r.fare_inr} | {r.travel_date}")

session.close()