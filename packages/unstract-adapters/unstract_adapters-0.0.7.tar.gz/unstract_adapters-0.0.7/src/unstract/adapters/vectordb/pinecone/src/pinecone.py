import os
import time
from typing import Any, Optional

import pinecone
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.vector_stores.types import BasePydanticVectorStore
from unstract.adapters.vectordb.vectordb_adapter import VectorDBAdapter


class Constants:
    API_KEY = "api_key"
    ENVIRONMENT = "environment"
    NAMESPACE = "namespace"
    DIMENSION = 1536
    METRIC = "euclidean"


class Pinecone(VectorDBAdapter):
    def __init__(self, settings: dict[str, Any]):
        super().__init__("Pinecone")
        self.config = settings

    @staticmethod
    def get_id() -> str:
        return "pinecone|83881133-485d-4ecc-b1f7-0009f96dc74a"

    @staticmethod
    def get_name() -> str:
        return "Pinecone"

    @staticmethod
    def get_description() -> str:
        return "Pinecone VectorDB"

    @staticmethod
    def get_icon() -> str:
        return (
            "https://storage.googleapis.com/pandora-static/"
            "adapter-icons/pinecone.png"
        )

    @staticmethod
    def get_json_schema() -> str:
        f = open(f"{os.path.dirname(__file__)}/static/json_schema.json")
        schema = f.read()
        f.close()
        return schema

    def get_vector_db_instance(self) -> Optional[BasePydanticVectorStore]:
        pinecone.init(
            api_key=str(self.config.get(Constants.API_KEY)),
            environment=str(self.config.get(Constants.ENVIRONMENT)),
        )
        pinecone.create_index(
            "unstract-1", dimension=Constants.DIMENSION, metric=Constants.METRIC
        )
        time.sleep(10)
        vector_db = PineconeVectorStore(
            api_key=str(self.config.get(Constants.API_KEY)),
            environment=str(self.config.get(Constants.ENVIRONMENT)),
        )
        return vector_db

    def test_connection(self) -> bool:
        vector_db = self.get_vector_db_instance()
        if vector_db is not None:
            return True
        else:
            return False
