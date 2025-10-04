from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import joblib
import pandas as pd
import sys
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.data_loader import load_data
from src.forecast import recursive_forecast

app = FastAPI(
    title="Zephra AQI Forecasting API", 
    version="1.0.0",
    description="ML-powered AQI forecasting service"
)

# Add CORS middleware for web frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load the model once at startup with error handling
try:
    model = joblib.load("models/gbr_model.pkl")
    logger.info("Model loaded successfully")
except Exception as e:
    logger.error(f"Failed to load model: {e}")
    model = None

@app.get("/")
def root():
    """Root endpoint with API information"""
    return {
        "message": "Zephra AQI Forecasting API", 
        "version": "1.0.0",
        "status": "running",
        "model_loaded": model is not None
    }

@app.get("/health")
def health_check():
    """Health check endpoint for monitoring and deployment"""
    try:
        # Check if model is loaded
        if model is None:
            raise HTTPException(status_code=503, detail="Model not loaded")
        
        # Test data loading (quick check)
        df = load_data(max_retries=1, timeout=10)
        if df is None or df.empty:
            return {"status": "degraded", "model": "ok", "data": "unavailable"}
        
        return {
            "status": "healthy", 
            "model": "loaded", 
            "data": "available",
            "data_rows": len(df)
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")

@app.get("/predict")
def predict():
    """Predict AQI for the next hour based on latest data"""
    try:
        if model is None:
            raise HTTPException(status_code=503, detail="Model not available")
        
        df = load_data()
        if df is None or df.empty:
            raise HTTPException(status_code=503, detail="Unable to fetch data")
        
        # Get the latest row and remove non-feature columns
        latest = df.drop(columns=['aqi', 'timestamp']).iloc[[-1]]
        pred = model.predict(latest)[0]
        
        return {
            "next_hour_AQI": round(pred, 1),
            "timestamp": df['timestamp'].iloc[-1].isoformat(),
            "confidence": "high"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@app.get("/forecast")
def forecast():
    """Generate 24-hour AQI forecast"""
    try:
        if model is None:
            raise HTTPException(status_code=503, detail="Model not available")
        
        df = load_data()
        if df is None or df.empty:
            raise HTTPException(status_code=503, detail="Unable to fetch data")
        
        # Get the latest row as feature vector
        latest = df.drop(columns=['aqi', 'timestamp']).iloc[[-1]].values
        preds = recursive_forecast(latest, steps=24)
        
        # Round predictions for better readability
        preds_rounded = [round(pred, 1) for pred in preds]
        
        return {
            "forecast_24h": preds_rounded,
            "base_timestamp": df['timestamp'].iloc[-1].isoformat(),
            "forecast_hours": 24,
            "model": "GradientBoostingRegressor"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Forecast error: {e}")
        raise HTTPException(status_code=500, detail=f"Forecast failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)