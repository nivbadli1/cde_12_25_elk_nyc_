from elasticsearch import Elasticsearch

# ============================================================
# Query 1 — Filter trips by passenger count and payment type
# ------------------------------------------------------------
# Demonstrates a Bool query with 'must' clauses.
# Both conditions must be true for a document to match.
#
# Run AFTER 02_consumer.py has indexed some data.
# ============================================================

# ---- Connect to Elasticsearch ----
es = Elasticsearch([{"host": "elasticsearch", "port": 9200, "scheme": "http"}])
INDEX_NAME = "nyctaxi"

# ---- Build the query ----
# Bool query with two 'must' conditions (equivalent to AND):
#   1. passenger_count == "1"
#   2. payment_type    == "2"
#
# We use the .keyword sub-field because the raw field is 'text'
# (analyzed/tokenized). The .keyword version is the exact, unanalyzed
# value -- required for exact-match term queries.
query_body = {
    "query": {
        "bool": {
            "must": [
                {"term": {"passenger_count.keyword": "1"}},
                {"term": {"payment_type.keyword": "2"}}
            ]
        }
    }
}

# ---- Execute the query ----
response = es.search(index=INDEX_NAME, body=query_body)

# ---- Print results ----
# response['hits']['hits'] is a list of matching documents.
# Each hit has '_source' which is the original indexed document.
print(f"Found {response['hits']['total']['value']} matching trips:\n")
for hit in response["hits"]["hits"]:
    print(hit["_source"])
