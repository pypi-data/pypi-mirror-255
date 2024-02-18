import os
from typing import Any, Optional

import weaviate
from llama_index.vector_stores import WeaviateVectorStore
from llama_index.vector_stores.types import BasePydanticVectorStore
from unstract.adapters.vectordb.constants import VectorDbConstants
from unstract.adapters.vectordb.helper import VectorDBHelper
from unstract.adapters.vectordb.vectordb_adapter import VectorDBAdapter


class Constants:
    URL = "url"
    API_KEY = "api_key"


class Weaviate(VectorDBAdapter):
    def __init__(self, settings: dict[str, Any]):
        super().__init__("Weaviate")
        self.config = settings

    @staticmethod
    def get_id() -> str:
        return "weaviate|294e08df-4e4a-40f2-8f0d-9e4940180ccc"

    @staticmethod
    def get_name() -> str:
        return "Weaviate"

    @staticmethod
    def get_description() -> str:
        return "Weaviate VectorDB"

    @staticmethod
    def get_icon() -> str:
        return (
            "https://storage.googleapis.com/pandora-static/"
            "adapter-icons/Weaviate.png"
        )

    @staticmethod
    def get_json_schema() -> str:
        f = open(f"{os.path.dirname(__file__)}/static/json_schema.json")
        schema = f.read()
        f.close()
        return schema

    def get_vector_db_instance(self) -> Optional[BasePydanticVectorStore]:
        collection_name = VectorDBHelper.get_collection_name(
            self.config.get(VectorDbConstants.VECTOR_DB_NAME_PREFIX),
            self.config.get(VectorDbConstants.EMBEDDING_TYPE),
        )
        client = weaviate.Client(
            url=str(self.config.get(Constants.URL)),
            auth_client_secret=weaviate.AuthApiKey(
                api_key=str(self.config.get(Constants.API_KEY))
            ),
        )
        vector_db = WeaviateVectorStore(
            collection_name=collection_name, weaviate_client=client
        )
        return vector_db

    def test_connection(self) -> bool:
        vector_db = self.get_vector_db_instance()
        if vector_db is not None:
            return True
        else:
            return False
