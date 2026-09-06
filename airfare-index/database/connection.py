import os
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import BigInteger, Column, DateTime, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

# Replace YOUR_POSTGRES_PASSWORD with the password you set during installation
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://postgres:YOUR_POSTGRES_PASSWORD@localhost:5432/airfare_db"
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

def init_db():
    Base.metadata.create_all(bind=engine)
    print("Database connection established and table verified/created.")