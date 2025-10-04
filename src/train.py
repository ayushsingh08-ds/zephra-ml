import joblib
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import numpy as np
from data_loader import load_data

# Load data from the API
df = load_data()

# Prepare features and target
# Use 'aqi' (lowercase) as target, and exclude timestamp
X = df.drop(columns=['aqi', 'timestamp'])
y = df['aqi']

# Split the data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Create and train the model
model = GradientBoostingRegressor(
    n_estimators=200, 
    learning_rate=0.05,
    max_depth=5, 
    subsample=0.8, 
    random_state=42
)

print("Training the model...")
model.fit(X_train, y_train)

# Evaluate the model
preds = model.predict(X_test)
rmse = np.sqrt(mean_squared_error(y_test, preds))
print(f"RMSE: {rmse}")

# Save the trained model
joblib.dump(model, "models/gbr_model.pkl")
print("Model saved to models/gbr_model.pkl")