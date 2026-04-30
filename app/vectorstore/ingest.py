import os
import hashlib
import json
import chromadb
from sentence_transformers import SentenceTransformer

CHROMA_PATH = "chroma_db"
COLLECTION_NAME = "esg_best_practices_v1"
METADATA_FILE = os.path.join(CHROMA_PATH, "metadata.json")


class ESGIngestor:

    def __init__(self):
        self.client = chromadb.PersistentClient(path=CHROMA_PATH)

        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME
        )

        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    # --------------------------
    # 🔒 Fingerprint (avoid re-ingestion)
    # --------------------------
    def _compute_fingerprint(self, texts):
        combined = "".join(texts)
        return hashlib.md5(combined.encode()).hexdigest()

    def _is_already_ingested(self, fingerprint):
        if not os.path.exists(METADATA_FILE):
            return False

        with open(METADATA_FILE) as f:
            data = json.load(f)

        return data.get("fingerprint") == fingerprint

    def _save_fingerprint(self, fingerprint):
        os.makedirs(CHROMA_PATH, exist_ok=True)
        with open(METADATA_FILE, "w") as f:
            json.dump({"fingerprint": fingerprint}, f)

    # --------------------------
    # ✂️ Chunking
    # --------------------------
    def chunk_text(self, text, chunk_size=512, overlap=64):
        words = text.split()
        chunks = []

        for i in range(0, len(words), chunk_size - overlap):
            chunk = " ".join(words[i:i + chunk_size])
            chunks.append(chunk)

        return chunks

    # --------------------------
    # 🚀 Ingest
    # --------------------------
    def ingest(self, documents):

        """
        documents = [
            {
                "text": "...",
                "source": "GRI",
                "kpi_tag": "emissions",
                "year": 2023
            }
        ]
        """

        all_chunks = []
        metadatas = []

        for doc in documents:
            chunks = self.chunk_text(doc["text"])

            for chunk in chunks:
                all_chunks.append(chunk)
                metadatas.append({
                    "source": doc["source"],
                    "kpi_tag": doc["kpi_tag"],
                    "year": doc["year"]
                })

        # 🔒 fingerprint check
        fingerprint = self._compute_fingerprint(all_chunks)

        if self._is_already_ingested(fingerprint):
            print("✅ Already ingested. Skipping.")
            return

        embeddings = self.model.encode(all_chunks).tolist()

        ids = [f"id_{i}" for i in range(len(all_chunks))]

        self.collection.add(
            documents=all_chunks,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )

        self._save_fingerprint(fingerprint)
        print("✅ Ingestion complete")