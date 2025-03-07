import streamlit as st
import math
from datetime import datetime, timedelta
import pytz  # For timezone handling

# Function for logarithmic calculation
def logarithmic_calculation(start_price, end_price, start_time, end_time, target_time):
    """
    Calculate the predicted price using logarithmic scaling.
    """
    # Calculate the logarithmic slope
    log_start_price = math.log(start_price)
    log_end_price = math.log(end_price)
    slope = (log_end_price - log_start_price) / (end_time - start_time)
    
    # Calculate the predicted price
    log_predicted_price = log_start_price + slope * (target_time - start_time)
    predicted_price = math.exp(log_predicted_price)
    
    return predicted_price

# Function for Auto Fit to Screen (linear calculation)
def auto_fit_to_screen_calculation(start_price, end_price, start_time, end_time, target_time):
    """
    Calculate the predicted price using linear scaling.
    """
    # Calculate the linear slope
    slope = (end_price - start_price) / (end_time - start_time)
    
    # Calculate the predicted price
    predicted_price = start_price + slope * (target_time - start_time)
    
    return predicted_price

# Function to get the start of a specific timeframe (corrected for PKT)
def get_timeframe_start(timeframe):
    """
    Calculate the start of the specified timeframe, aligned with Pakistan Time (PKT).
    """
    # Get current time in UTC
    now_utc = datetime.now(pytz.utc)
    # Convert to Pakistan Time (PKT)
    pkt = pytz.timezone("Asia/Karachi")
    now = now_utc.astimezone(pkt)

    if timeframe == "monthly":
        # Monthly candles start at 05:00 PKT on the 1st of the month
        return now.replace(day=1, hour=5, minute=0, second=0, microsecond=0)
    elif timeframe == "weekly":
        # Weekly candles start on Monday at 05:00 PKT
        return (now - timedelta(days=now.weekday())).replace(hour=5, minute=0, second=0, microsecond=0)
    elif timeframe == "daily":
        # Daily candles start at 05:00 PKT
        return now.replace(hour=5, minute=0, second=0, microsecond=0)
    elif timeframe == "4hourly":
        # 4-hourly candles start at 01:00, 05:00, 09:00, etc. PKT
        start_hour = ((now.hour - 1) // 4) * 4 + 1  # Adjusted for 01:00 start
        return now.replace(hour=start_hour, minute=0, second=0, microsecond=0)
    elif timeframe == "1hourly":
        # 1-hourly candles start at the top of the hour
        return now.replace(minute=0, second=0, microsecond=0)
    elif timeframe == "15min":
        # 15-minute candles start at 00, 15, 30, 45 minutes
        start_minute = (now.minute // 15) * 15
        return now.replace(minute=start_minute, second=0, microsecond=0)
    elif timeframe == "1min":
        # 1-minute candles start at the top of the minute
        return now.replace(second=0, microsecond=0)
    else:
        return now

# Streamlit app layout
st.title("Trendline Prediction App")

# Input fields for the user with default values
st.sidebar.header("Input Parameters")

# Default values
default_start_price = 1.0  # Simple default value
default_end_price = 10.0   # Simple default value
default_start_datetime = "2025-01-01 05:00"
default_end_datetime = "2025-03-01 05:00"
default_target_datetime = "2025-03-07 05:00"

# Input fields with simple defaults but support for decimals
start_price = st.sidebar.number_input("Start Price", value=default_start_price, step=0.00000001, format="%f")
end_price = st.sidebar.number_input("End Price", value=default_end_price, step=0.00000001, format="%f")

# Date and time input using text_input (with default values)
start_datetime_str = st.sidebar.text_input("Start Time (YYYY-MM-DD HH:MM)", value=default_start_datetime)
end_datetime_str = st.sidebar.text_input("End Time (YYYY-MM-DD HH:MM)", value=default_end_datetime)
target_datetime_str = st.sidebar.text_input("Target Time (YYYY-MM-DD HH:MM)", value=default_target_datetime)

# Convert date-time strings to timestamps
try:
    # Parse input dates in PKT
    pkt = pytz.timezone("Asia/Karachi")
    start_datetime = pkt.localize(datetime.strptime(start_datetime_str, "%Y-%m-%d %H:%M"))
    end_datetime = pkt.localize(datetime.strptime(end_datetime_str, "%Y-%m-%d %H:%M"))
    target_datetime = pkt.localize(datetime.strptime(target_datetime_str, "%Y-%m-%d %H:%M"))

    start_timestamp = start_datetime.timestamp()
    end_timestamp = end_datetime.timestamp()
    target_timestamp = target_datetime.timestamp()

except ValueError:
    st.error("Invalid date or time format. Please use 'YYYY-MM-DD HH:MM'.")
    st.stop()

# Auto Detect Button for Multiple Timeframes
if st.button("Auto Detect"):
    # Define timeframes
    timeframes = [
        ("Monthly", "monthly"),
        ("Weekly", "weekly"),
        ("Daily", "daily"),
        ("4-Hourly", "4hourly"),
        ("1-Hourly", "1hourly"),
        ("15-Minute", "15min"),
        ("1-Minute", "1min")
    ]

    # Display predictions in a clean layout
    st.header("Predicted Prices for Current Timeframes")
    for name, timeframe in timeframes:
        # Get the start of the timeframe
        start_of_timeframe = get_timeframe_start(timeframe)
        target_timestamp = start_of_timeframe.timestamp()

        # Calculate predicted prices
        predicted_price_log = logarithmic_calculation(start_price, end_price, start_timestamp, end_timestamp, target_timestamp)
        predicted_price_linear = auto_fit_to_screen_calculation(start_price, end_price, start_timestamp, end_timestamp, target_timestamp)

        # Display results in a clean card-like layout
        st.subheader(f"{name} Prediction")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Logarithmic", f"{predicted_price_log:.10f}")
        with col2:
            st.metric("Linear", f"{predicted_price_linear:.10f}")
        st.write(f"Timeframe Start: {start_of_timeframe.strftime('%Y-%m-%d %H:%M')}")
        st.write("---")

# Buttons for manual calculations
if st.button("Logarithmic Calculation"):
    predicted_price = logarithmic_calculation(start_price, end_price, start_timestamp, end_timestamp, target_timestamp)
    st.success(f"Predicted Price (Logarithmic): {predicted_price:.10f}")

if st.button("Auto Fit to Screen Calculation"):
    predicted_price = auto_fit_to_screen_calculation(start_price, end_price, start_timestamp, end_timestamp, target_timestamp)
    st.success(f"Predicted Price (Linear): {predicted_price:.10f}")