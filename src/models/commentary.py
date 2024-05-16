import logging

import chromadb

logger = logging.getLogger(__name__)


class CommentaryModel:
    def __init__(self) -> None:
        client = chromadb.HttpClient(
            host='localhost',
            port=8000,
            settings=chromadb.Settings(anonymized_telemetry=False)
        )
        self.collection = client.get_or_create_collection(
            name="Baseline",
            metadata={"hnsw:space": "cosine"}
        )
        self.initialize()

    def initialize(self):
        self.generate_commentary([0.0] * 420)
        logger.info("Commentary model initialized")

    def generate_commentary(self, embedding: list[float]) -> str:
        response = self.collection.query(
            query_embeddings=embedding,
            n_results=1
        )
        commentary = response["documents"][0][0]
        return commentary    
