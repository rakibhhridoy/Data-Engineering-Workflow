from kafka import KafkaProducer
import requests
import time
import json

# Alpha Vantage API details
API_KEY = "API_KEY"
SYMBOL = "IBM"  # Stock symbol
INTERVAL = "1min"  # Data interval
TOPIC = "stock_data"

# Kafka producer
producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
)

def fetch_stock_data():
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={SYMBOL}&interval={INTERVAL}&apikey={API_KEY}"
    response = requests.get(url)
    data = response.json()
    print("API Response:", data)  # Print the entire API response

    # Handle rate limit messages
    if "Information" in data:
        print("Rate limit exceeded or invalid API call:", data["Information"])
        return None
    elif "Error Message" in data:
        print("Error:", data["Error Message"])
        return None
    elif "Note" in data:  # Rate limit message
        print("Note:", data["Note"])
        return None
    elif "Time Series (1min)" not in data:
        print("Unexpected API response structure.")
        return None

    return data["Time Series (1min)"]

def produce_to_kafka():
    while True:
        stock_data = fetch_stock_data()
        if stock_data:
            for timestamp, values in stock_data.items():
                message = {
                    "symbol": SYMBOL,
                    "timestamp": timestamp,
                    "open": values["1. open"],
                    "high": values["2. high"],
                    "low": values["3. low"],
                    "close": values["4. close"],
                    "volume": values["5. volume"],
                }
                producer.send(TOPIC, value=message)
                print(f"Produced: {message}")
        time.sleep(12)  # Wait 12 seconds to avoid rate limits

if __name__ == "__main__":
    produce_to_kafka()