import requests
import pandas as pd
import logging
import time
import os
from typing import Optional

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_data(max_retries: int = 3, timeout: int = 30) -> Optional[pd.DataFrame]:
    """
    Fetch data from the Zephra API dashboard endpoint with error handling.
    Returns a pandas DataFrame with merged data from different sources.
    
    Args:
        max_retries: Maximum number of retry attempts
        timeout: Request timeout in seconds
    
    Returns:
        DataFrame with merged data or None if failed
    """
    url = os.getenv('ZEPHRA_API_URL', 'https://zephra.onrender.com/api/dashboard')
    
    for attempt in range(max_retries):
        try:
            logger.info(f"Fetching data from API (attempt {attempt + 1}/{max_retries})")
            
            # Add timeout and proper error handling
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()  # Raises HTTPError for bad responses
            
            data = response.json()
            
            # Validate response structure
            required_keys = ["weather", "air_quality", "satellite", "health"]
            missing_keys = [key for key in required_keys if key not in data]
            if missing_keys:
                raise ValueError(f"Missing keys in API response: {missing_keys}")
            
            # Extract data from different sources
            weather_df = pd.DataFrame(data["weather"])
            air_quality_df = pd.DataFrame(data["air_quality"])
            satellite_df = pd.DataFrame(data["satellite"])
            health_df = pd.DataFrame(data["health"])
            
            # Check if dataframes are empty
            if any(df.empty for df in [weather_df, air_quality_df, satellite_df, health_df]):
                raise ValueError("One or more data sources returned empty data")
            
            # Convert timestamps to datetime and round to nearest hour for merging
            for df_temp in [weather_df, air_quality_df, satellite_df, health_df]:
                if 'timestamp' not in df_temp.columns:
                    raise ValueError("Missing timestamp column in data")
                
                df_temp['timestamp'] = pd.to_datetime(df_temp['timestamp'])
                df_temp['timestamp_hour'] = df_temp['timestamp'].dt.floor('h')
            
            # Merge all data on rounded timestamp
            df = weather_df.merge(air_quality_df, on='timestamp_hour', how='inner', suffixes=('_weather', '_air'))
            df = df.merge(satellite_df, on='timestamp_hour', how='inner', suffixes=('', '_sat'))
            df = df.merge(health_df, on='timestamp_hour', how='inner', suffixes=('', '_health'))
            
            # Check if merge resulted in data
            if df.empty:
                raise ValueError("Data merge resulted in empty dataset - timestamp alignment issue")
            
            # Clean up timestamp columns - keep just one
            df['timestamp'] = df['timestamp_weather']
            timestamp_cols = [col for col in df.columns if 'timestamp' in col and col != 'timestamp']
            df = df.drop(columns=timestamp_cols)
            
            # Clean column names and remove duplicate source columns
            columns_to_drop = [col for col in df.columns if 'data_source' in col]
            df = df.drop(columns=columns_to_drop, errors='ignore')
            
            logger.info(f"Successfully loaded {len(df)} rows of data")
            return df
            
        except requests.exceptions.Timeout:
            logger.warning(f"Request timeout on attempt {attempt + 1}")
        except requests.exceptions.ConnectionError:
            logger.warning(f"Connection error on attempt {attempt + 1}")
        except requests.exceptions.HTTPError as e:
            logger.warning(f"HTTP error on attempt {attempt + 1}: {e}")
        except ValueError as e:
            logger.error(f"Data validation error: {e}")
            return None  # Don't retry for data validation errors
        except Exception as e:
            logger.error(f"Unexpected error on attempt {attempt + 1}: {e}")
        
        if attempt < max_retries - 1:
            sleep_time = 2 ** attempt  # Exponential backoff
            logger.info(f"Retrying in {sleep_time} seconds...")
            time.sleep(sleep_time)
    
    logger.error("Failed to load data after all retry attempts")
    return None