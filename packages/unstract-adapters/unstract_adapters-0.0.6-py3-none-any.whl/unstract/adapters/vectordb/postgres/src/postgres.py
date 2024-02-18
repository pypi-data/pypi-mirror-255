import os
from typing import Any, Optional

from llama_index.vector_stores import PGVectorStore
from llama_index.vector_stores.types import BasePydanticVectorStore
from unstract.adapters.vectordb.constants import VectorDbConstants
from unstract.adapters.vectordb.helper import VectorDBHelper
from unstract.adapters.vectordb.vectordb_adapter import VectorDBAdapter


class Constants:
    DATABASE = "database"
    HOST = "host"
    PASSWORD = "password"
    PORT = "port"
    USER = "user"
    DIM_VALUE = 1536


class Postgres(VectorDBAdapter):
    def __init__(self, settings: dict[str, Any]):
        super().__init__("Postgres")
        self.config = settings

    @staticmethod
    def get_id() -> str:
        return "postgres|70ab6cc2-e86a-4e5a-896f-498a95022d34"

    @staticmethod
    def get_name() -> str:
        return "Postgres"

    @staticmethod
    def get_description() -> str:
        return "Postgres VectorDB"

    @staticmethod
    def get_icon() -> str:
        return (
            "https://storage.googleapis.com/pandora-static/"
            "adapter-icons/postgres.png"
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
        vector_db = PGVectorStore.from_params(
            database=self.config.get(Constants.DATABASE),
            host=str(self.config.get(Constants.HOST)),
            password=str(self.config.get(Constants.PASSWORD)),
            port=str(self.config.get(Constants.PORT)),
            user=str(self.config.get(Constants.USER)),
            table_name=collection_name,
        )
        # Other fields that need looking into are
        # perform_setup
        # schema_name
        # embed_dim=768 BYe default, Postgres always creates collections
        # of vector_size=1536 Collection name has an additional prefix of data_
        return vector_db

    def test_connection(self) -> bool:
        vector_db = self.get_vector_db_instance()
        test_result: bool = VectorDBHelper.test_vector_db_instance(
            vector_store=vector_db
        )
        return test_result
