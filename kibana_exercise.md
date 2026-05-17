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

## Payment Type Reference

| Code | Meaning |
|------|---------|
| 1 | Credit card |
| 2 | Cash |
| 3 | No charge |
| 4 | Dispute |
| 5 | Unknown |
| 6 | Voided trip |
