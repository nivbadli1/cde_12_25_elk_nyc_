from elasticsearch import Elasticsearch

# ============================================================
# Query 3 — Aggregation: average fare amount by payment type
# ------------------------------------------------------------
# Demonstrates a nested aggregation:
#   outer bucket  --> Terms  (group by payment_type)
#   inner metric  --> Avg    (average fare per group)
#
# Equivalent SQL:
#   SELECT payment_type, AVG(CAST(fare_amount AS FLOAT))
#   FROM nyctaxi GROUP BY payment_type
#
# The fare_amount field was stored as a string (keyword) by Elasticsearch
# because it came in as text from the API. We use a Painless script to
# cast it to a number at query time.
#
# Run AFTER 02_consumer.py has indexed some data.
# ============================================================

# ---- Connect to Elasticsearch ----
es = Elasticsearch([{"host": "elasticsearch", "port": 9200, "scheme": "http"}])
INDEX_NAME = "nyctaxi"

# ---- Build the nested aggregation query ----
query_body = {
    "size": 0,  # Only return aggregation results, not individual documents

    "aggs": {
        # Outer aggregation: group documents by payment_type
        "avg_fare_by_payment_type": {
            "terms": {
                "field": "payment_type.keyword"
            },

            # Inner aggregation: for each payment_type bucket, compute average fare
            "aggs": {
                "average_fare": {
                    "avg": {
                        # Painless script: Elasticsearch's built-in scripting language.
                        # Used here because fare_amount is stored as a string keyword,
                        # so we need to manually parse it to a float before averaging.
                        # The try/catch handles any values that can't be parsed (nulls, etc.)
                        "script": {
                            "source": """
                                if (doc['fare_amount.keyword'].size() > 0 && !doc['fare_amount.keyword'].empty) {
                                    try {
                                        return Double.parseDouble(doc['fare_amount.keyword'].value);
                                    } catch (Exception e) {
                                        return null;
                                    }
                                } else {
                                    return null;
                                }
                            """
                        }
                    }
                }
            }
        }
    }
}

# ---- Execute the query ----
response = es.search(index=INDEX_NAME, body=query_body)

# ---- Print results ----
# Each bucket = one payment_type group with its average fare
print("Average fare amount by payment type:\n")
for bucket in response["aggregations"]["avg_fare_by_payment_type"]["buckets"]:
    avg = bucket["average_fare"]["value"]
    avg_display = f"{avg:.2f}" if avg is not None else "N/A"
    print(f"  Payment Type: {bucket['key']}  |  Average Fare: ${avg_display}")


# ---- Equivalent Kibana Dev Tools query ----
# POST /nyctaxi/_search
# {
#   "size": 0,
#   "aggs": {
#     "avg_fare_by_payment_type": {
#       "terms": { "field": "payment_type.keyword" },
#       "aggs": {
#         "average_fare": {
#           "avg": {
#             "script": {
#               "source": """
#                 if (doc['fare_amount.keyword'].size() > 0 && !doc['fare_amount.keyword'].empty) {
#                   try { return Double.parseDouble(doc['fare_amount.keyword'].value); }
#                   catch (Exception e) { return null; }
#                 } else { return null; }
#               """
#             }
#           }
#         }
#       }
#     }
#   }
# }
