#!/bin/bash

# Zephra ML Deployment Script
# This script trains the model and starts the API server

echo "🚀 Starting Zephra ML Deployment..."

# Install dependencies if requirements.txt exists
if [ -f "requirements.txt" ]; then
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt
fi

# Train the model
echo "🧠 Training the ML model..."
python src/train.py

# Check if model was created successfully
if [ ! -f "models/gbr_model.pkl" ]; then
    echo "❌ Model training failed! Exiting..."
    exit 1
fi

echo "✅ Model training completed successfully!"

# Start the API server
echo "🌐 Starting API server on port 8080..."
uvicorn api.app:app --host 0.0.0.0 --port 8080