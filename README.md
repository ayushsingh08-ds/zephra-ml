# Zephra ML - AQI Forecasting Service

A machine learning service for forecasting Air Quality Index (AQI) values using gradient boosting regression.

## 🚀 Features

- Fetches real-time data from Zephra API
- Trains a Gradient Boosting Regressor model
- Provides single-hour and 24-hour AQI forecasts
- FastAPI-based REST API
- Docker containerization support

## 📁 Project Structure

```
zephra-ml/
├── data/                   # (optional) store local datasets if needed
├── models/
│   └── gbr_model.pkl       # trained model
├── src/
│   ├── data_loader.py      # fetch from /api/dashboard
│   ├── train.py            # training + save model
│   └── forecast.py         # 24h recursive forecast
├── api/
│   └── app.py              # FastAPI/Flask app
├── requirements.txt        # dependencies
├── Dockerfile              # for deployment
├── run.sh                  # deployment script
└── README.md               # usage instructions
```

## 🛠️ Setup & Installation

### Prerequisites

- Python 3.9+
- pip

### Installation

1. Clone or download the project
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Quick Start

**For Windows:**

```cmd
.\run.bat
```

**For Linux/Mac:**

```bash
./run.sh
```

This will automatically:

1. Install all dependencies
2. Train the model with fresh data from the Zephra API
3. Start the API server on http://localhost:8080

**Test the API:**

```bash
python test_api.py
```

## 🔧 Usage

### Training the Model

First, train the model with the latest data:

```bash
python src/train.py
```

This will:

- Fetch data from the Zephra API
- Train a Gradient Boosting Regressor
- Save the model to `models/gbr_model.pkl`
- Display training RMSE

### Running the API

#### Local Development

```bash
uvicorn api.app:app --host 0.0.0.0 --port 8080 --reload
```

#### Using Docker

```bash
docker build -t zephra-ml .
docker run -p 8080:8080 zephra-ml
```

#### One-Command Deployment

Use the provided script:

```bash
./run.sh
```

## 📡 API Endpoints

### GET `/`

Returns API information and version.

### GET `/predict`

Returns AQI prediction for the next hour.

**Response:**

```json
{
  "next_hour_AQI": 85.3
}
```

### GET `/forecast`

Returns 24-hour AQI forecast.

**Response:**

```json
{
  "forecast_24h": [85.3, 87.1, 89.2, ...]
}
```

## 🔄 Model Details

- **Algorithm:** Gradient Boosting Regressor
- **Parameters:**
  - n_estimators: 200
  - learning_rate: 0.05
  - max_depth: 5
  - subsample: 0.8
- **Features:** All columns except AQI, timestamp, and location
- **Target:** AQI values

## 🚀 Deployment

### Render/Heroku

1. Push code to your repository
2. Connect to Render/Heroku
3. Use the `run.sh` script as your start command
4. Set environment variables if needed

### Docker

```bash
docker build -t zephra-ml .
docker run -p 8080:8080 zephra-ml
```

## 📊 Model Performance

The model's performance is evaluated using RMSE (Root Mean Square Error) on the test set. Training metrics are displayed during model training.

## 🔧 Configuration

- **Data Source:** https://zephra.onrender.com/api/dashboard
- **Model Storage:** `models/gbr_model.pkl`
- **API Port:** 8080
- **Host:** 0.0.0.0 (for Docker compatibility)

## 📝 Notes

- The model assumes the last feature in the dataset is the lag AQI value for recursive forecasting
- Adjust the column names in `data_loader.py` and training scripts based on your actual API response structure
- The forecast uses recursive prediction where each prediction becomes input for the next step
