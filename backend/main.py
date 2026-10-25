from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend.data_pipeline import run_pipeline

app = FastAPI(title="Wind Forecast Accuracy API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/api/forecast-accuracy")
def get_forecast_accuracy():
    try:
        return run_pipeline()
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Failed to calculate forecast accuracy"
        ) from exc