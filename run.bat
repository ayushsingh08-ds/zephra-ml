@echo off
REM Zephra ML Deployment Script for Windows
REM This script trains the model and starts the API server

echo 🚀 Starting Zephra ML Deployment...

REM Install dependencies if requirements.txt exists
if exist "requirements.txt" (
    echo 📦 Installing dependencies...
    pip install -r requirements.txt
)

REM Train the model
echo 🧠 Training the ML model...
python src/train.py

REM Check if model was created successfully
if not exist "models/gbr_model.pkl" (
    echo ❌ Model training failed! Exiting...
    exit /b 1
)

echo ✅ Model training completed successfully!

REM Start the API server
echo 🌐 Starting API server on port 8080...
uvicorn api.app:app --host 0.0.0.0 --port 8080