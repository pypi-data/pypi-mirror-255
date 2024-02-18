import os
from typing import Any, Optional

from llama_index.vector_stores import MilvusVectorStore
from llama_index.vector_stores.types import VectorStore
from unstract.adapters.vectordb.constants import VectorDbConstants
from unstract.adapters.vectordb.helper import VectorDBHelper
from unstract.adapters.vectordb.vectordb_adapter import VectorDBAdapter


class Constants:
    URI = "uri"
    TOKEN = "token"
    DIM_VALUE = 1536


class Milvus(VectorDBAdapter):
    def __init__(self, settings: dict[str, Any]):
        super().__init__("Milvus")
        self.config = settings

    @staticmethod
    def get_id() -> str:
        return "milvus|3f42f6f9-4b8e-4546-95f3-22ecc9aca442"

    @staticmethod
    def get_name() -> str:
        return "Milvus"

    @staticmethod
    def get_description() -> str:
        return "Milvus VectorDB"

    @staticmethod
    def get_icon() -> str:
        return (
            "https://storage.googleapis.com/pandora-static/"
            "adapter-icons/Milvus.png"
        )

    @staticmethod
    def get_json_schema() -> str:
        f = open(f"{os.path.dirname(__file__)}/static/json_schema.json")
        schema = f.read()
        f.close()
        return schema

    def get_vector_db_instance(self) -> Optional[VectorStore]:
        collection_name = VectorDBHelper.get_collection_name(
            self.config.get(VectorDbConstants.VECTOR_DB_NAME_PREFIX),
            self.config.get(VectorDbConstants.EMBEDDING_TYPE),
        )
        vector_db = MilvusVectorStore(
            collection_name=collection_name,
            dim=Constants.DIM_VALUE,
        )
        return vector_db

    def test_connection(self) -> bool:
        vector_db = self.get_vector_db_instance()
        if vector_db is not None:
            return True
        else:
            return False
