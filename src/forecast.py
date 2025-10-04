import joblib
import numpy as np

def recursive_forecast(X_last, steps=24):
    """
    Perform recursive forecasting for the specified number of steps.
    
    Args:
        X_last: Latest feature vector (numpy array)
        steps: Number of hours to forecast (default: 24)
    
    Returns:
        List of predicted AQI values
    """
    model = joblib.load("models/gbr_model.pkl")
    preds = []
    X_input = X_last.copy()
    
    for _ in range(steps):
        y_pred = model.predict(X_input)[0]
        preds.append(y_pred)
        # For simplicity, we'll keep the same features for each prediction
        # In a real scenario, you'd update time-dependent features
        # X_input could be modified based on domain knowledge
    
    return preds