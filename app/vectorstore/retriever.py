import chromadb
from sentence_transformers import SentenceTransformer

CHROMA_PATH = "chroma_db"
COLLECTION_NAME = "esg_best_practices_v1"


class ChromaRetriever:

    def __init__(self):
        self.client = chromadb.PersistentClient(path=CHROMA_PATH)

        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME
        )

        self.model = SentenceTransformer("all-MiniLM-L6-v2")

        # 🔥 Debug: check DB is not empty
        try:
            print(f"📦 Chroma collection count: {self.collection.count()}")
        except Exception:
            print("⚠️ Could not fetch collection count")

    def query(self, kpi_tag, top_k=3):

        print(f"\n🔍 Querying for KPI: {kpi_tag}")

        query_embedding = self.model.encode(kpi_tag).tolist()

        # -------------------------------
        # 1️⃣ Try STRICT filter
        # -------------------------------
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where={"kpi_tag": kpi_tag}
        )

        docs = self._parse_results(results)

        if docs:
            print("✅ Found results with strict filter")
            return docs

        print("⚠️ No results with strict filter — retrying without filter")

        # -------------------------------
        # 2️⃣ Fallback: NO filter
        # -------------------------------
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )

        docs = self._parse_results(results)

        if docs:
            print("✅ Found results without filter")
            return docs

        print("❌ No documents found at all")

        return [{
            "text": "No best practice found",
            "source": "N/A",
            "year": 0,
            "kpi_tag": kpi_tag
        }]

    # -------------------------------
    # 🔧 Helper: Parse results safely
    # -------------------------------
    def _parse_results(self, results):

        print("RAW RESULTS:", results)

        if not results.get("documents") or not results["documents"][0]:
            return []

        docs = []

        for i in range(len(results["documents"][0])):
            docs.append({
                "text": results["documents"][0][i],
                "source": results["metadatas"][0][i].get("source", "unknown"),
                "year": results["metadatas"][0][i].get("year", "unknown"),
                "kpi_tag": results["metadatas"][0][i].get("kpi_tag", "unknown")
            })

        return docs