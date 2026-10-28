from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import json
from pathlib import Path
from data_pipeline import run_pipeline

app = FastAPI(title="Wind Forecast Accuracy API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "abcde-zvkw.vercel.app"
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)
    

RESULTS_FILE = Path(__file__).parent / "january_results.json"


@app.get("/api/forecast-accuracy")
def get_forecast_accuracy():
    if not RESULTS_FILE.exists():
        raise HTTPException(
            status_code=503,
            detail="Saved results are not available yet.",
        )

    try:
        with RESULTS_FILE.open("r", encoding="utf-8") as file:
            return json.load(file)
    except (OSError, json.JSONDecodeError) as exc:
        raise HTTPException(
            status_code=500,
            detail="Could not load saved results.",
        ) from exc