import os
from typing import Any, Optional

from llama_index.llms.llm import LLM
from llama_index.llms.mistral import MistralAI
from unstract.adapters.llm.helper import LLMHelper
from unstract.adapters.llm.llm_adapter import LLMAdapter


class Constants:
    MODEL = "model"
    API_KEY = "api_key"


class MistralLLM(LLMAdapter):
    def __init__(self, settings: dict[str, Any]):
        super().__init__("Mistral")
        self.config = settings

    @staticmethod
    def get_id() -> str:
        return "mistral|00f766a5-6d6d-47ea-9f6c-ddb1e8a94e82"

    @staticmethod
    def get_name() -> str:
        return "Mistral AI"

    @staticmethod
    def get_description() -> str:
        return "Mistral AI LLM"

    @staticmethod
    def get_icon() -> str:
        return (
            "https://storage.googleapis.com/pandora-static/"
            "adapter-icons/Mistral%20AI.png"
        )

    @staticmethod
    def get_json_schema() -> str:
        f = open(f"{os.path.dirname(__file__)}/static/json_schema.json")
        schema = f.read()
        f.close()
        return schema

    def get_llm_instance(self) -> Optional[LLM]:
        llm = MistralAI(
            model=str(self.config.get(Constants.MODEL)),
            api_key=str(self.config.get(Constants.API_KEY)),
            temperature=0,
        )
        return llm

    def test_connection(self) -> bool:
        llm = self.get_llm_instance()
        test_result: bool = LLMHelper.test_llm_instance(llm=llm)
        return test_result
