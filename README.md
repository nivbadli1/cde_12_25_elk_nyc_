# NYC Taxi — Kafka + Elasticsearch Pipeline

A hands-on data pipeline that streams NYC Taxi trip data from a public API into Elasticsearch via Kafka, then runs queries and aggregations on the indexed data.

---

## Architecture

```
NYC Open Data API
       │  HTTP GET (JSON array)
       ▼
 01_producer.py        ← sends each trip as a Kafka message
       │  Kafka topic: "my_trip"
       ▼
 02_consumer.py        ← reads from Kafka, indexes into Elasticsearch
       │  ES index: "nyctaxi"
       ▼
 Elasticsearch
       │
       ├── 03_filter_query.py   (bool / must filter)
       ├── 04_vendor_agg.py     (terms aggregation)
       └── 05_fare_agg.py       (nested avg aggregation + Painless script)
```

---

## Requirements

- Python 3.7+
- Kafka broker running at `course-kafka:9092`
- Elasticsearch 7.x running at `elasticsearch:9200`
- Kibana (optional — for visual exploration)

Install Python dependencies:

```bash
pip install -r requirements.txt
```

---

## Run Order

### Step 1 — Start the producer

Fetches trip records from the NYC Open Data API and sends them to the Kafka topic `my_trip`.

```bash
python 01_producer.py
```

Keep this running in a terminal. It loops continuously and fetches new batches every few seconds.

### Step 2 — Start the consumer (new terminal)

Reads messages from the Kafka topic and indexes each trip as a document in the `nyctaxi` Elasticsearch index.

```bash
python 02_consumer.py
```

Keep this running alongside the producer. You should see indexed documents being printed.

### Step 3 — Run queries (any order, new terminal)

Once data is flowing into Elasticsearch, run any of the query scripts:

```bash
# Filter trips by passenger count and payment type
python 03_filter_query.py

# Count total trips grouped by vendor
python 04_vendor_agg.py

# Average fare amount grouped by payment type
python 05_fare_agg.py
```

---

## File Reference

| File | Description |
|------|-------------|
| `01_producer.py` | Fetches from NYC API → sends to Kafka |
| `02_consumer.py` | Reads from Kafka → indexes to Elasticsearch |
| `03_filter_query.py` | Bool query: filter by passenger count + payment type |
| `04_vendor_agg.py` | Terms aggregation: trip count per vendor |
| `05_fare_agg.py` | Nested aggregation: avg fare per payment type (Painless script) |
| `requirements.txt` | Python dependencies |

---

## Kibana — Dev Tools

You can run the same queries directly in Kibana's Dev Tools console.

**Check index exists and see document count:**
```
GET /nyctaxi/_count
```

**See the index mapping (field types):**
```
GET /nyctaxi/_mapping
```

**Filter query (same as 03_filter_query.py):**
```
POST /nyctaxi/_search
{
  "query": {
    "bool": {
      "must": [
        { "term": { "passenger_count.keyword": "1" } },
        { "term": { "payment_type.keyword": "2" } }
      ]
    }
  }
}
```

**Trips by vendor (same as 04_vendor_agg.py):**
```
POST /nyctaxi/_search
{
  "size": 0,
  "aggs": {
    "trips_by_vendor": {
      "terms": { "field": "vendorid.keyword" }
    }
  }
}
```

---

## Key Concepts

**Why `.keyword`?**
Elasticsearch stores text fields in two ways: analyzed (tokenized, for full-text search) and `.keyword` (exact, unanalyzed). For aggregations and exact-match `term` queries we always use `.keyword`.

**Why Painless script in query 3?**
The `fare_amount` field was ingested as a string (the API returned it as text). Since it was mapped as a keyword, we can't use a standard `avg` metric directly — we use a Painless script to cast it to a float at query time.

**Why `size: 0` in aggregations?**
We only care about the aggregation results, not the individual documents. Setting `size: 0` tells Elasticsearch not to return the hits array, which makes the response smaller and faster.
