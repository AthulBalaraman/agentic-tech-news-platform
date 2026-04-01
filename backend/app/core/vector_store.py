import os
import chromadb
from .config import get_settings

settings = get_settings()

class VectorStore:
    def __init__(self):
        os.makedirs(settings.CHROMA_DB_DIR, exist_ok=True)
        # Initialize a persistent local ChromaDB instance
        self.client = chromadb.PersistentClient(path=settings.CHROMA_DB_DIR)
        
        # This collection stores the technical context of past summaries
        self.collection = self.client.get_or_create_collection(
            name="tech_context",
            metadata={"hnsw:space": "cosine"} # Use Cosine similarity
        )

    def add_insight(self, id: str, text: str, metadata: dict):
        self.collection.add(
            documents=[text],
            metadatas=[metadata],
            ids=[id]
        )

    def search_similar(self, text: str, n_results: int = 1):
        if self.collection.count() == 0:
            return {"distances": [[]]}
        return self.collection.query(
            query_texts=[text],
            n_results=n_results
        )

    def clear(self):
        """Delete all vectors and recreate the collection."""
        try:
            self.client.delete_collection("tech_context")
            self.collection = self.client.get_or_create_collection(
                name="tech_context",
                metadata={"hnsw:space": "cosine"}
            )
        except Exception as e:
            print(f"⚠️ Error clearing ChromaDB: {e}")

vector_store = VectorStore()
