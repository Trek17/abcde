# UK Wind Forecast Accuracy Dashboard

A full-stack analytics dashboard for evaluating the accuracy of day-ahead national wind generation forecasts in Great Britain using data from the **Elexon BMRS API**.

## Overview

Wind generation forecasts help energy suppliers estimate how much electricity will be available to meet demand. Forecast errors can affect procurement decisions and balancing requirements.

This application compares forecast wind generation with actual generation for January 2026, calculates forecast error metrics, and visualizes performance over a selected date range.

### Key Features

- **Forecast vs. actual:** Interactive time-series chart comparing hourly wind generation.
- **Performance metrics:** Mean Absolute Error (MAE) and Root Mean Squared Error (RMSE).
- **Date filtering:** Select a date range and recalculate metrics for the selected period.
- **Hourly data table:** Inspect actual generation, forecast generation, and forecast error.
- **Interactive tooltips:** View detailed values for individual observations.
- **Precomputed results:** Cache evaluation results to reduce repeated API requests and improve response times.
- **Docker support:** Run the frontend and backend in containers.

## Tech Stack

| Component   | Technologies                   |
| ----------- | ------------------------------ |
| Frontend    | React, Vite, Recharts          |
| Backend     | Python, FastAPI, Pandas, NumPy |
| Data source | Elexon BMRS API                |
| Deployment  | Docker, Docker Compose         |

## Data Sources

The application uses two Elexon datasets:

- **WINDFOR:** Day-ahead wind generation forecasts.
- **FUELHH:** Half-hourly actual generation by fuel type, filtered to wind.

The evaluation covers delivery hours in January 2026.

## Methodology

### 1. Forecast selection

For each delivery hour, the application selects the latest available forecast published before the assumed decision cutoff of **06:00 GMT on the preceding day**.

This cutoff is a modelling assumption used to evaluate forecast performance at a consistent point before delivery.

### 2. Actual generation aggregation

FUELHH actual generation is recorded at half-hourly intervals. The two half-hourly observations are averaged to obtain hourly actual generation. Hours without both expected observations are excluded.

### 3. Forecast alignment

Hourly forecasts are matched to hourly actual generation using their delivery start times. Only matching observations within January 2026 are evaluated.

### 4. Error metrics

Forecast error is defined as:

`Error = Actual Generation − Forecast Generation`

- **Positive error:** Actual generation exceeded the forecast.
- **Negative error:** Actual generation was below the forecast.

### Error Metrics

**Mean Absolute Error (MAE)** measures the average magnitude of forecast errors:

```text
MAE = (1/n) × Σ |Aᵢ − Fᵢ|
```

**Root Mean Squared Error (RMSE)** penalizes larger errors more heavily:

```text
RMSE = √[(1/n) × Σ (Aᵢ − Fᵢ)²]
```

Where:

- `Aᵢ` = actual generation for hour `i`
- `Fᵢ` = forecast generation for hour `i`
- `n` = number of evaluated hours

Both metrics are expressed in **MW**. Lower values indicate better forecast accuracy.

## Architecture

```text
Elexon BMRS API
       |
       v
Python Data Pipeline
       |
       v
Data Cleaning and Alignment
       |
       v
Forecast Evaluation
(MAE, RMSE, Hourly Errors)
       |
       v
Precomputed JSON Results
       |
       v
FastAPI Backend
       |
       v
React Dashboard
(Chart, Metrics, Filters, Table)
```

## Getting Started

### Prerequisites

- Python 3.12+
- Node.js and npm
- Docker and Docker Compose (for containerized execution)

### Run with Docker

From the project root, run:

```bash
docker compose up --build
```

Then open:

- **Dashboard:** http://localhost:3000
- **API endpoint:** http://localhost:8000/api/forecast-accuracy
- **API documentation:** http://localhost:8000/docs

To stop the containers:

```bash
docker compose down
```

### Run locally without Docker

**1. Start the backend**

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python precompute.py
uvicorn main:app --reload --port 8000
```

On Windows, activate the environment with:

```powershell
.venv\Scripts\Activate.ps1
```

**2. Start the frontend in a separate terminal**

```bash
cd frontend
npm install
npm run dev
```

Open the local URL printed by Vite, usually http://localhost:5173.

## API

### `GET /api/forecast-accuracy`

Returns the precomputed evaluation results.

The response contains:

- `summary`: Number of evaluated hours, MAE, and RMSE.
- `hourly`: Delivery timestamps, actual generation, forecast generation, and forecast error.
- `period_performance`: Aggregated performance by settlement period.

## Assumptions and Limitations

- The decision cutoff of 06:00 GMT on the preceding day is an evaluation assumption.
- Forecast records are selected based on publication time and delivery start time.
- WINDFOR values are treated as hourly forecasts corresponding to their delivery start times.
- Actual generation is calculated from complete pairs of half-hourly observations.
- The evaluation covers January 2026 and should not be interpreted as a live forecasting service.
- Results depend on the availability and consistency of the underlying Elexon data.

## Future Improvements

- Compare forecast accuracy across different forecast publication cutoffs.
- Expand evaluation to additional months and compare forecast performance over time.

## AI Tool Disclosure

AI tools were used to assist with development, debugging, and documentation.

## Data Attribution

Data provided by [Elexon BMRS](https://bmrs.elexon.co.uk/).
