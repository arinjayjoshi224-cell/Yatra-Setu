# 🛫 Airfare Price Index (API-IN)

A real-time econometric pipeline that scrapes Indian domestic flight fares, persists microdata in PostgreSQL, computes a geometric **Jevons Price Index** (mirroring CPI elementary aggregate methodology), and exposes the metrics via FastAPI and an interactive Streamlit dashboard.

---

## 🛠️ Architecture & Tech Stack

* **Web Scraping:** Playwright (Chromium automation with HTTP/2 protocol bypass)
* **Storage:** PostgreSQL + SQLAlchemy ORM
* **Econometrics Engine:** Jevons Geometric Mean Index calculation
* **API Service:** FastAPI + Uvicorn (OpenAPI/Swagger docs)
* **Frontend:** Streamlit + Plotly interactive charts

---

## 📋 Prerequisites

Ensure the following are installed on your machine:
1. **Python 3.10+**
2. **PostgreSQL** (running locally on port `5432`)
3. **Git**

---

## 🚀 Setup & Execution Guide

### 1. Clone the Repository
```bash
git clone [https://github.com/avira/Yatra-Setu.git](https://github.com/avira/Yatra-Setu.git)
cd Yatra-Setu/airfare-index

##2 Create and activate virtual environment :

python -m venv venv
.\venv\Scripts\Activate.ps1

##3 Install modules: 

pip install playwright sqlalchemy psycopg2-binary pydantic python-dotenv fastapi uvicorn streamlit requests plotly
playwright install chromium

## 4Configure Database & Environment
Open PostgreSQL (psql or pgAdmin) and create a database:

SQL
CREATE DATABASE airfare_db;
Create a .env file inside the airfare-index/ directory:

Code snippet
DATABASE_URL=postgresql://postgres:<YOUR_POSTGRES_PASSWORD>@localhost:5432/airfare_db
(Replace <YOUR_POSTGRES_PASSWORD> with your local PostgreSQL password).

Initialize the database tables:

Bash
python -c "from database.connection import init_db; init_db()"

🔄 Running the Pipeline
Step A: Scrape Live Flight Fares
Scrape live flight records for the DEL -> BOM corridor and store them in PostgreSQL:

Bash
python -m scraper.yatra_scraper

Step B: Compute the Jevons Price Index
Calculate the matched-model geometric price relatives and save the index calculation:

Bash
python -m analytics.index_calculator

Step C: Launch the API Server
Start the FastAPI service:

Bash
uvicorn api.main:app --reload --port 8000
Live API Root: http://127.0.0.1:8000

Interactive Swagger Documentation: http://127.0.0.1:8000/docs
