from app.vectorstore.retriever import ChromaRetriever

retriever = ChromaRetriever()

results = retriever.query("scope1_tco2e")

print("\n=== RETRIEVER OUTPUT ===")
for r in results:
    print(r)