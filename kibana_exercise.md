# Kibana Exercise — NYC Taxi Data
### Big Data Engineering Course

> **Before you start:** Make sure `01_producer.py` and `02_consumer.py` are both running,
> and that data is visible in the `nyctaxi` index.
> Open Kibana → **Dev Tools** (the wrench icon in the left sidebar).

---

## Part 1 — Getting to Know the Index

### Exercise 1.1 — Check the index exists

Run the following and confirm you get a `count > 0`:

```
GET /nyctaxi/_count
```

**Question:** How many documents are currently in the index?

---

### Exercise 1.2 — Explore the field mapping

```
GET /nyctaxi/_mapping
```

**Questions:**
- What type is the `fare_amount` field? Why is it not a number?
- What is the difference between a `text` field and a `keyword` field?
- Why do we use `fare_amount.keyword` in our queries?

---

### Exercise 1.3 — Fetch a sample document

```
GET /nyctaxi/_search
{
  "size": 3
}
```

Look at one document in the `_source` field.

**Question:** What fields does a taxi trip have? Write down at least 5.

---

## Part 2 — Filtering (WHERE)

### Exercise 2.1 — Filter by vendor

Find all trips from vendor `1`:

```
GET /nyctaxi/_search
{
  "query": {
    "term": {
      "vendorid.keyword": "1"
    }
  }
}
```

**Question:** How many hits did you get?

---

### Exercise 2.2 — Filter with two conditions (AND)

Find all trips where:
- `passenger_count` is `2`
- `payment_type` is `1`

> Hint: use a `bool` query with `must`

<details>
<summary>Show answer</summary>

```
GET /nyctaxi/_search
{
  "query": {
    "bool": {
      "must": [
        { "term": { "passenger_count.keyword": "2" } },
        { "term": { "payment_type.keyword": "1" } }
      ]
    }
  }
}
```
</details>

---

### Exercise 2.3 — Your turn

Write a query that returns trips where `store_and_fwd_flag` is `"N"`.

---

## Part 3 — Aggregations (GROUP BY)

### Exercise 3.1 — Count trips per payment type

```
GET /nyctaxi/_search
{
  "size": 0,
  "aggs": {
    "trips_by_payment": {
      "terms": {
        "field": "payment_type.keyword"
      }
    }
  }
}
```

**Questions:**
- Which payment type has the most trips?
- What does `"size": 0` do and why do we use it here?

---

### Exercise 3.2 — Count trips per number of passengers

Write an aggregation that groups trips by `passenger_count`.

> Hint: copy the query above and change the field name.

<details>
<summary>Show answer</summary>

```
GET /nyctaxi/_search
{
  "size": 0,
  "aggs": {
    "trips_by_passengers": {
      "terms": {
        "field": "passenger_count.keyword"
      }
    }
  }
}
```
</details>

**Question:** What is the most common number of passengers per trip?

---

### Exercise 3.3 — Nested aggregation

Group trips by vendor, and for each vendor show the breakdown by payment type:

```
GET /nyctaxi/_search
{
  "size": 0,
  "aggs": {
    "by_vendor": {
      "terms": {
        "field": "vendorid.keyword"
      },
      "aggs": {
        "by_payment": {
          "terms": {
            "field": "payment_type.keyword"
          }
        }
      }
    }
  }
}
```

**Question:** For vendor `2`, which payment type is most common?

---

## Part 4 — Discover & Visualize (Kibana UI)

> Switch from Dev Tools to the **Discover** tab.

### Exercise 4.1 — Create an index pattern

1. Go to **Stack Management → Index Patterns**
2. Create a new pattern: `nyctaxi`
3. Skip the time field (our data has no timestamp)

### Exercise 4.2 — Explore in Discover

1. Open **Discover** and select the `nyctaxi` index pattern
2. Find the `fare_amount` field in the left panel — pin it to the table
3. Add `vendorid` and `passenger_count` to the table as well

**Question:** Can you spot any trips with unusually high or low fares?

### Exercise 4.3 — Build a pie chart

1. Go to **Visualize → Create visualization → Pie**
2. Select the `nyctaxi` index
3. Add a bucket: **Split slices → Terms → `payment_type.keyword`**
4. Click **Update**

**Question:** What percentage of trips used payment type `1`?

---

## Bonus Challenge

Write a query that returns only trips where the `trip_distance` is greater than `5`.

> Hint: `trip_distance` is stored as a keyword string, so you'll need a **script-based filter** or a **range query on the keyword** — or explore whether the field has a numeric mapping.

<details>
<summary>Show answer</summary>

```
GET /nyctaxi/_search
{
  "query": {
    "script": {
      "script": {
        "source": "Double.parseDouble(doc['trip_distance.keyword'].value) > 5"
      }
    }
  }
}
```
</details>

---

---

## Part 5 — Building a Dashboard

> We will build a dashboard with **4 visualizations** and assemble them into one screen.
> Each visualization is created separately in **Visualize**, then added to a **Dashboard**.
>
> Make sure you already created the `nyctaxi` index pattern in Exercise 4.1.

---

### Visualization 1 — Pie chart: trips by payment type

**Goal:** See the share of each payment method across all trips.

**Steps:**
1. Go to **Visualize → Create visualization → Pie**
2. Select index: `nyctaxi`
3. Under **Buckets** click **Add → Split slices**
4. Aggregation: `Terms`
5. Field: `payment_type.keyword`
6. Size: `6` (to show all payment types)
7. Click **Update ▶**
8. Click **Save** → name it `Trips by Payment Type`

<details>
<summary>Expected result ✅</summary>

You should see a pie divided into slices — typically 2 dominant slices:
- **Type 1** (Credit card) — usually the largest slice (~60–70%)
- **Type 2** (Cash) — second largest (~25–35%)
- Types 3, 4, 5, 6 — small or absent depending on data volume

The legend on the right maps each color to a payment type code.
</details>

---

### Visualization 2 — Vertical bar chart: trips by vendor

**Goal:** Compare how many trips each vendor has.

**Steps:**
1. Go to **Visualize → Create visualization → Vertical Bar**
2. Select index: `nyctaxi`
3. Y-axis is already set to `Count` — leave it as is
4. Under **Buckets** click **Add → X-axis**
5. Aggregation: `Terms`
6. Field: `vendorid.keyword`
7. Order by: `Metric: Count` → Descending
8. Size: `5`
9. Click **Update ▶**
10. Click **Save** → name it `Trips by Vendor`

<details>
<summary>Expected result ✅</summary>

Two bars on the X-axis — one for vendor `1` and one for vendor `2`.
The height of each bar = number of trips for that vendor.
Vendor `2` is usually higher in this dataset.

If you see only one bar, it means all sampled trips belong to one vendor — normal with a small dataset.
</details>

---

### Visualization 3 — Metric: total number of trips

**Goal:** Show a single large number — total documents in the index.

**Steps:**
1. Go to **Visualize → Create visualization → Metric**
2. Select index: `nyctaxi`
3. The default metric is already `Count` — leave it as is
4. Click **Update ▶**
5. (Optional) Under **Options** set the font size to `60`
6. Click **Save** → name it `Total Trips`

<details>
<summary>Expected result ✅</summary>

A large number displayed in the center of the panel — total documents in `nyctaxi`.

The number will grow over time as the producer keeps sending data.
Refresh after a few minutes to see it increase.
</details>

---

### Visualization 4 — Data table: trip count by payment type

**Goal:** Show a table with each payment type and its trip count.

**Steps:**
1. Go to **Visualize → Create visualization → Data Table**
2. Select index: `nyctaxi`
3. Under **Buckets** click **Add → Split rows**
4. Aggregation: `Terms`
5. Field: `payment_type.keyword`
6. Size: `6`
7. Click **Update ▶**
8. Click **Save** → name it `Payment Type Table`

<details>
<summary>Expected result ✅</summary>

A table with two columns:

| payment_type.keyword | Count |
|---|---|
| 1 | (number of credit card trips) |
| 2 | (number of cash trips) |
| 3 | (no charge trips) |

**Teaching moment:** Notice we can't show average fare directly here — because
`fare_amount` was auto-mapped as `keyword` (string), not `float`.
This is a very common real-world mistake when ingesting data without a predefined mapping.

The fix is to define the mapping **before** indexing any data:

```
PUT /nyctaxi
{
  "mappings": {
    "properties": {
      "fare_amount":     { "type": "float" },
      "trip_distance":   { "type": "float" },
      "passenger_count": { "type": "integer" }
    }
  }
}
```

Once the mapping is explicit, the standard `avg` metric works without any Painless script.
</details>

---

### Assemble the Dashboard

**Goal:** Combine all 4 visualizations into one screen.

**Steps:**
1. Go to **Dashboard → Create new dashboard**
2. Click **Add** (top right corner)
3. Add all 4 saved visualizations:
   - `Total Trips`
   - `Trips by Payment Type`
   - `Trips by Vendor`
   - `Payment Type Table`
4. Drag and resize the panels into this layout:

```
┌──────────────┬─────────────────────────┐
│ Total Trips  │   Trips by Payment Type │
│   (Metric)   │        (Pie chart)      │
├──────────────┴─────────────────────────┤
│  Trips by Vendor   │  Payment Type     │
│   (Bar chart)      │  Table            │
└────────────────────┴───────────────────┘
```

5. Set auto-refresh: top right → **Auto refresh → 10 seconds**
6. Click **Save** → name it `NYC Taxi Overview`

<details>
<summary>Expected result ✅</summary>

A live dashboard that updates every 10 seconds.
You can watch the `Total Trips` metric increase in real time as the producer keeps sending messages through Kafka into Elasticsearch.

This is the core of what Kibana is built for — turning a stream of raw events into a live operational view.
</details>

---

### Dashboard — Discussion Questions

After building the dashboard, discuss these with the class:

**1. Why does the pie chart show codes (1, 2, 3) instead of names (Credit card, Cash)?**

> Because Elasticsearch stores exactly what it received from the API — raw codes.
> Translating codes to labels would happen in the application layer, or via a
> Kibana **scripted field** (Stacks Management → Index Patterns → Scripted fields).

**2. The Total Trips metric keeps growing after a restart — why?**

> Because `auto_offset_reset='earliest'` in the consumer means every restart
> re-reads all messages from offset 0, creating **duplicate documents** in Elasticsearch.
> Elasticsearch auto-generates a new `_id` for each call to `es.index()`, so duplicates are not detected.
>
> Fix: pass a stable `id` to `es.index()` — for example the Kafka offset:
> ```python
> es.index(index=ES_INDEX, id=message.offset, body=document)
> ```
> Now re-indexing the same offset overwrites the same document instead of creating a duplicate.

**3. What would you need to change to show Average Fare in the table?**

> Define an explicit `float` mapping for `fare_amount` before indexing (see Visualization 4 answer).
> Then delete the index, restart the consumer, and the standard `avg` metric will work
> in Kibana without needing a Painless script.

**4. What happens to the dashboard if the producer stops?**

> The data already in Elasticsearch stays — the dashboard keeps showing the last state.
> Nothing is lost. This is one of the key advantages of a Kafka buffer:
> the producer and consumer are fully decoupled.

---


## Payment Type Reference

| Code | Meaning |
|------|---------|
| 1 | Credit card |
| 2 | Cash |
| 3 | No charge |
| 4 | Dispute |
| 5 | Unknown |
| 6 | Voided trip |
