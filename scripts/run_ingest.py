import json
from app.vectorstore.ingest import ESGIngestor

with open("data/esg_docs.json") as f:
    docs = json.load(f)

ingestor = ESGIngestor()
ingestor.ingest(docs)