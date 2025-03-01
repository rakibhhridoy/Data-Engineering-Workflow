from kafka import KafkaConsumer
import psycopg2
import json

# Kafka consumer
consumer = KafkaConsumer(
    "stock_data",
    bootstrap_servers="localhost:9092",
    value_deserializer=lambda v: json.loads(v.decode("utf-8")),
)

# PostgreSQL connection
conn = psycopg2.connect(
    dbname="mydatabase",
    user="admin",
    password="password",
    host="localhost",
    port="5432",
)
cursor = conn.cursor()

# Create table if not exists
cursor.execute("""
    CREATE TABLE IF NOT EXISTS stock_data (
        symbol TEXT,
        timestamp TIMESTAMP,
        open FLOAT,
        high FLOAT,
        low FLOAT,
        close FLOAT,
        volume BIGINT,
        PRIMARY KEY (symbol, timestamp)
    )
""")
conn.commit()

def consume_from_kafka():
    for message in consumer:
        data = message.value
        cursor.execute("""
            INSERT INTO stock_data (symbol, timestamp, open, high, low, close, volume)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (symbol, timestamp) DO NOTHING
        """, (
            data["symbol"],
            data["timestamp"],
            data["open"],
            data["high"],
            data["low"],
            data["close"],
            data["volume"],
        ))
        conn.commit()
        print(f"Consumed and stored: {data}")

if __name__ == "__main__":
    consume_from_kafka()