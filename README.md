# UK Wind Forecast Accuracy Dashboard

A full-stack application that evaluates day-ahead wind generation forecasts against actual wind generation in Great Britain for January 2026. It presents forecast accuracy metrics and hourly forecast-versus-actual comparisons using data from the Elexon API.

## Live Application

- **Frontend:** https://abcde-zvkw.vercel.app/
- **Backend API:** https://abcde-lemon-seven.vercel.app/api/forecast-accuracy

## Features

- Evaluates hourly wind generation forecasts against actual generation.
- Displays Mean Absolute Error (MAE) and Root Mean Squared Error (RMSE), measured in MW.
- Visualizes forecast and actual generation over time.
- Provides hourly forecast error data for further analysis.
- Uses precomputed January 2026 results to avoid fetching and processing the full dataset on every request.

## Technology Stack

- **Frontend:** React, TypeScript, Vite
- **Backend:** Python, FastAPI
- **Data processing:** Pandas
- **Data source:** Elexon Insights API
- **Deployment:** Vercel
- **Containerization:** Docker and Docker Compose

## Project Structure

```text
.
├── backend/
│   ├── main.py                 # FastAPI application and API endpoint
│   ├── pipeline.py             # Fetches, processes, and evaluates data
│   ├── precompute.py           # Generates the January results cache
│   ├── january_results.json    # Precomputed evaluation results
│   ├── requirements.txt        # Python dependencies
│   └── Dockerfile              # Backend container configuration
│
├── frontend/
│   ├── src/                    # React application source code
│   ├── public/                 # Static assets
│   ├── package.json            # Frontend dependencies and scripts
│   ├── package-lock.json       # Locked npm dependency versions
│   ├── vite.config.ts          # Vite configuration
│   ├── index.html              # Frontend HTML entry point
│   └── Dockerfile              # Frontend container configuration
│
├── docker-compose.yml          # Runs the application containers
└── README.md                   # Project documentation
```

_Note: The tree lists the main project files; retain only paths that match the actual repository._

## How to Run the Application

### Option 1: Run with Docker (Recommended)

**Prerequisites:** Docker Desktop or Docker Engine with Docker Compose.

1. Clone the repository:

   ```bash
   git clone <YOUR_PUBLIC_GITHUB_REPOSITORY_URL>
   cd <YOUR_REPOSITORY_DIRECTORY>
   ```

2. Build and start the application:

   ```bash
   docker compose up --build
   ```

3. Open the application:

   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000/api/forecast-accuracy

To stop the application, run:

```bash
docker compose down
```

### Option 2: Run Locally Without Docker

**Prerequisites:** Python 3.12+, Node.js, and npm.

#### Start the backend

1. Open a terminal in the repository root.
2. Create and activate a Python virtual environment:

   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate
   ```

   On Windows, activate it with:

   ```powershell
   .venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Start FastAPI:

   ```bash
   uvicorn main:app --reload --port 8000
   ```

   The API will be available at http://localhost:8000/api/forecast-accuracy.

#### Start the frontend

Open a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open the local URL printed by Vite, typically http://localhost:5173.

If necessary, configure the frontend's `VITE_API_URL` environment variable to point to the backend:

```text
VITE_API_URL=http://localhost:8000
```

Restart the Vite development server after changing environment variables.

## API Endpoint

### `GET /api/forecast-accuracy`

Returns the January 2026 forecast evaluation results, including summary metrics, hourly observations, and performance breakdowns.

Example response structure:

```json
{
  "summary": {
    "evaluated_hours": 743,
    "mae_mw": 2138.95,
    "rmse_mw": 2636.8
  },
  "hourly": [],
  "period_performance": []
}
```

The hourly array contains actual generation, forecast generation, and forecast error for each evaluated hour. The values above are an example of the current cached summary; the endpoint returns the complete dataset.

## Data Processing and Methodology

1. Retrieve day-ahead wind generation forecasts from Elexon's `WINDFOR` dataset.
2. Retrieve actual half-hourly wind generation from the `FUELHH` dataset.
3. Aggregate actual generation into hourly averages, retaining hours with exactly two half-hourly observations.
4. For each delivery hour, select the latest forecast published on or before the assumed decision cutoff.
5. Match forecasts with actual generation by delivery timestamp and evaluate January 2026.

The forecast error is defined as:

```text
Error = Actual Generation - Forecast Generation
```

- Positive error: generation was underforecast.
- Negative error: generation was overforecast.

The evaluation metrics are:

```text
MAE  = Mean of absolute forecast errors
RMSE = Square root of the mean squared forecast errors
```

Both metrics are expressed in MW. MAE measures the average absolute error, while RMSE penalizes larger errors more heavily.

### Decision Cutoff Assumption

The application uses **06:00 GMT on the day before delivery** as an assumed forecast decision cutoff. This is a modelling assumption for the analysis, not a claim that Elexon or the electricity market specifies this as the official deadline.

## Data Source

Forecast and generation data are sourced from the [Elexon Insights API](https://www.elexon.co.uk/data/).

## Limitations

- The analysis covers January 2026 only.
- Evaluation is limited to delivery hours with matching forecasts and valid hourly actual generation.
- Results depend on the selected decision-cutoff assumption and the availability and publication timestamps of source data.
- The deployed API serves precomputed results; refreshing the page does not trigger a complete data refresh.

## AI Tool Disclosure

AI tools were used to assist with development, debugging, and documentation.
