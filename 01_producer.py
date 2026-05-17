from kafka import KafkaProducer
import time
import json
import requests
from datetime import datetime

# ============================================================
# NYC Taxi Data Producer
# ------------------------------------------------------------
# This script fetches NYC Taxi trip data from the NYC Open Data
# API and sends each trip record as a message to a Kafka topic.
#
# Flow: NYC Open Data API --> KafkaProducer --> topic "my_trip"
# ============================================================

# Kafka configuration
KAFKA_BOOTSTRAP_SERVERS = "course-kafka:9092"
KAFKA_TOPIC = "my_trip"
NYC_TAXI_API_URL = "https://data.cityofnewyork.us/resource/gi8d-wdg5.json"

# ---- Initialize the Kafka producer ONCE (outside the loop) ----
# Creating the producer inside the loop would open a new TCP
# connection for every single message -- very slow and wasteful.
producer = KafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS)

print(f"Producer started. Sending to topic: '{KAFKA_TOPIC}'")

while True:
    try:
        # ---- Fetch data from the NYC Open Data API ----
        # The API returns a JSON array where each element is one taxi trip.
        response = requests.get(url=NYC_TAXI_API_URL, timeout=10)
        response.raise_for_status()   # raises an exception for 4xx/5xx HTTP errors
        trips = response.json()
        print(f"[{datetime.now()}] Fetched {len(trips)} records from API")

        # ---- Send each trip record to Kafka ----
        # Kafka works with bytes, so we:
        #   1. Serialize the Python dict to a JSON string (json.dumps)
        #   2. Encode the string to bytes               (.encode('utf-8'))
        for row in trips:
            producer.send(
                topic=KAFKA_TOPIC,
                value=json.dumps(row).encode('utf-8')
            )
            print(f"  Sent: {row}")
            time.sleep(1)   # Slow down so students can see messages arriving

        # ---- Flush ensures all buffered messages are actually sent ----
        producer.flush()
        print(f"[{datetime.now()}] Batch complete. Waiting 3 seconds...\n")

    except requests.exceptions.RequestException as e:
        # If the API is down or returns an error, log it and retry after 10 seconds
        print(f"[{datetime.now()}] API error: {e}. Retrying in 10 seconds...")
        time.sleep(10)
        continue

    time.sleep(3)
