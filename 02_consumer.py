from kafka import KafkaConsumer
from elasticsearch import Elasticsearch
import json

# ============================================================
# NYC Taxi Data Consumer
# ------------------------------------------------------------
# This script reads trip messages from a Kafka topic and indexes
# each one as a document in Elasticsearch.
#
# Flow: Kafka topic "my_trip" --> KafkaConsumer --> Elasticsearch index "nyctaxi"
#
# Run AFTER 01_producer.py is already running.
# ============================================================

# ---- Kafka configuration ----
KAFKA_TOPIC = "my_trip"
KAFKA_BOOTSTRAP_SERVERS = ["course-kafka:9092"]

# ---- Elasticsearch configuration ----
ES_INDEX = "nyctaxi"
es = Elasticsearch([{"host": "elasticsearch", "port": 9200, "scheme": "http"}])

# ---- Create a Kafka consumer ----
# auto_offset_reset='earliest' --> start reading from the very first
#   message in the topic (useful if the consumer starts after the producer)
# group_id --> Kafka tracks the offset per group, so if this consumer
#   restarts it will continue from where it stopped
# value_deserializer --> automatically decodes bytes to a Python dict
#   so message.value is already ready to index into Elasticsearch
consumer = KafkaConsumer(
    KAFKA_TOPIC,
    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
    auto_offset_reset="earliest",
    group_id="taxi_consumer",
    enable_auto_commit=True,
    value_deserializer=lambda x: json.loads(x.decode("utf-8"))
)

print(f"Consumer started. Listening on topic: '{KAFKA_TOPIC}'")
print(f"Indexing documents into Elasticsearch index: '{ES_INDEX}'\n")

# ---- Consume messages and index into Elasticsearch ----
# This loop runs forever -- each iteration handles one Kafka message.
# message.value is already a Python dict (thanks to value_deserializer).
# es.index() creates a new document in the 'nyctaxi' index.
# Elasticsearch auto-generates a unique _id for each document.
for message in consumer:
    document = message.value

    # Index the document into Elasticsearch
    # Note: the 'body' parameter is deprecated in ES client 8.x,
    # but works correctly with elasticsearch==7.13.2 used in this course.
    es.index(index=ES_INDEX, body=document)

    print(f"  Indexed offset {message.offset}: {document.get('vendorid', '?')} | "
          f"fare={document.get('fare_amount', '?')} | "
          f"passengers={document.get('passenger_count', '?')}")

print("Consumer stopped.")
