import os
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import BigInteger, Column, DateTime, Float, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://postgres:Arinjay@localhost:5432/airfare_db"
)

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class FlightPriceDB(Base):
    __tablename__ = "raw_airfare_records"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    source_platform = Column(String(50), default="Yatra")
    airline = Column(String(50), nullable=False)
    flight_number = Column(String(50))
    origin = Column(String(3), nullable=False)
    destination = Column(String(3), nullable=False)
    departure_time = Column(String(10))
    arrival_time = Column(String(10))
    fare_inr = Column(Integer, nullable=False)
    travel_date = Column(String(20), nullable=False)
    scraped_at = Column(DateTime, default=datetime.utcnow)

class CalculatedIndexDB(Base):
    __tablename__ = "airfare_price_indices"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    calculation_time = Column(DateTime, default=datetime.utcnow)
    route = Column(String(10), nullable=False)           # e.g., "DEL-BOM" or "ALL"
    time_horizon = Column(String(10), default="T+30")    # e.g., T+0, T+7, T+30
    index_type = Column(String(20), default="JEVONS")    # JEVONS, CARLI, DUTOT
    index_value = Column(Float, nullable=False)          # Baseline = 100.0
    matched_flight_count = Column(Integer, nullable=False)
    base_period = Column(DateTime, nullable=False)

def init_db():
    Base.metadata.create_all(bind=engine)
    print("Database tables verified/created successfully.")