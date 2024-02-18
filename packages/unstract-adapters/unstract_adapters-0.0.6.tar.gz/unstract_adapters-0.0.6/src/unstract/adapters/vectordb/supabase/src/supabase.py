import os
from typing import Any, Optional

from llama_index.vector_stores import SupabaseVectorStore
from llama_index.vector_stores.types import VectorStore
from unstract.adapters.vectordb.constants import VectorDbConstants
from unstract.adapters.vectordb.helper import VectorDBHelper
from unstract.adapters.vectordb.vectordb_adapter import VectorDBAdapter


class Constants:
    DATABASE = "database"
    HOST = "host"
    PASSWORD = "password"
    PORT = "port"
    USER = "user"
    COLLECTION_NAME = "base_demo"


class Supabase(VectorDBAdapter):
    def __init__(self, settings: dict[str, Any]):
        super().__init__("Supabase")
        self.config = settings

    @staticmethod
    def get_id() -> str:
        return "supabase|e6998e3c-3595-48c0-a190-188dbd803858"

    @staticmethod
    def get_name() -> str:
        return "Supabase"

    @staticmethod
    def get_description() -> str:
        return "Supabase VectorDB"

    @staticmethod
    def get_icon() -> str:
        return (
            "https://storage.googleapis.com/pandora-static/"
            "adapter-icons/supabase.png"
        )

    @staticmethod
    def get_json_schema() -> str:
        f = open(f"{os.path.dirname(__file__)}/static/json_schema.json")
        schema = f.read()
        f.close()
        return schema

    def get_vector_db_instance(self) -> Optional[VectorStore]:
        collection_name = self.config.get(Constants.DATABASE)
        if collection_name is None:
            collection_name = VectorDBHelper.get_collection_name(
                self.config.get(VectorDbConstants.VECTOR_DB_NAME_PREFIX),
                self.config.get(VectorDbConstants.EMBEDDING_TYPE),
            )
        else:
            collection_name = VectorDBHelper.get_collection_name(
                collection_name,
                self.config.get(VectorDbConstants.EMBEDDING_TYPE),
            )
        user = str(self.config.get(Constants.USER))
        password = str(self.config.get(Constants.PASSWORD))
        host = str(self.config.get(Constants.HOST))
        port = str(self.config.get(Constants.PORT))
        db_name = collection_name

        postgres_connection_string = (
            f"postgresql://{user}:{password}@{host}:{port}/{db_name}"
        )
        vector_db = SupabaseVectorStore(
            postgres_connection_string=postgres_connection_string,
            collection_name=Constants.COLLECTION_NAME,
        )
        return vector_db

    def test_connection(self) -> bool:
        vector_db = self.get_vector_db_instance()
        if vector_db is not None:
            return True
        else:
            return False
