from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database.connection import SessionLocal, CalculatedIndexDB, FlightPriceDB

app = FastAPI(
    title="Airfare Price Index (API-IN)",
    description="Real-time Indian Airfare Price Index & Microdata API",
    version="1.0.0"
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class IndexResponse(BaseModel):
    id: int
    route: str
    calculation_time: datetime
    time_horizon: str
    index_type: str
    index_value: float
    matched_flight_count: int
    base_period: datetime

    class Config:
        from_attributes = True

class RouteSummary(BaseModel):
    route: str
    total_observations: int
    min_fare: int
    avg_fare: float
    max_fare: int

@app.get("/")
def root():
    return {
        "service": "Airfare Price Index API (India)",
        "status": "online",
        "endpoints": ["/api/v1/indices", "/api/v1/summary", "/api/v1/latest"]
    }

@app.get("/api/v1/indices", response_model=List[IndexResponse])
def get_indices(
    route: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    query = db.query(CalculatedIndexDB)
    if route:
        query = query.filter(CalculatedIndexDB.route == route.upper())
    return query.order_by(CalculatedIndexDB.calculation_time.desc()).limit(limit).all()

@app.get("/api/v1/latest")
def get_latest_index(route: str = "DEL-BOM", db: Session = Depends(get_db)):
    latest = (
        db.query(CalculatedIndexDB)
        .filter(CalculatedIndexDB.route == route.upper())
        .order_by(CalculatedIndexDB.calculation_time.desc())
        .first()
    )
    if not latest:
        raise HTTPException(status_code=404, detail=f"No index records found for {route}")
    
    return {
        "route": latest.route,
        "index_type": latest.index_type,
        "index_value": latest.index_value,
        "calculation_time": latest.calculation_time,
        "sample_size": latest.matched_flight_count,
        "status": "normal"
    }

@app.get("/api/v1/summary", response_model=List[RouteSummary])
def get_market_summary(db: Session = Depends(get_db)):
    records = db.query(FlightPriceDB).all()
    if not records:
        return []

    grouped = {}
    for r in records:
        corridor = f"{r.origin}-{r.destination}"
        if corridor not in grouped:
            grouped[corridor] = []
        grouped[corridor].append(r.fare_inr)

    summary = []
    for corridor, fares in grouped.items():
        summary.append(
            RouteSummary(
                route=corridor,
                total_observations=len(fares),
                min_fare=min(fares),
                avg_fare=round(sum(fares) / len(fares), 2),
                max_fare=max(fares)
            )
        )
    return summary