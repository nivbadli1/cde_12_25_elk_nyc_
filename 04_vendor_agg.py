from elasticsearch import Elasticsearch

# ============================================================
# Query 2 — Aggregation: total trips by vendor
# ------------------------------------------------------------
# Demonstrates a Terms aggregation -- equivalent to
#   SELECT vendorid, COUNT(*) FROM nyctaxi GROUP BY vendorid
# in SQL.
#
# Run AFTER 02_consumer.py has indexed some data.
# ============================================================

# ---- Connect to Elasticsearch ----
es = Elasticsearch([{"host": "elasticsearch", "port": 9200, "scheme": "http"}])
INDEX_NAME = "nyctaxi"

# ---- Build the aggregation query ----
# "size": 0 means: don't return individual documents, only the aggregation result.
# "terms" aggregation groups documents by the unique values of a field,
# and counts how many documents fall into each group (bucket).
query_body = {
    "size": 0,
    "aggs": {
        "trips_by_vendor": {
            "terms": {
                "field": "vendorid.keyword"   # .keyword = exact match, not analyzed
            }
        }
    }
}

# ---- Execute the query ----
response = es.search(index=INDEX_NAME, body=query_body)

# ---- Print results ----
# response['aggregations']['trips_by_vendor']['buckets'] is a list of buckets.
# Each bucket has:
#   'key'       --> the vendor ID value
#   'doc_count' --> number of documents (trips) for that vendor
print("Total trips by vendor:\n")
for bucket in response["aggregations"]["trips_by_vendor"]["buckets"]:
    print(f"  Vendor ID: {bucket['key']}  |  Total Trips: {bucket['doc_count']}")


# ---- Equivalent Kibana Dev Tools query ----
# POST /nyctaxi/_search
# {
#   "size": 0,
#   "aggs": {
#     "trips_by_vendor": {
#       "terms": {
#         "field": "vendorid.keyword"
#       }
#     }
#   }
# }
