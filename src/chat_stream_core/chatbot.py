from chat_stream_core import propmts, history
from models import openai_client
from langchain_core.output_parsers import StrOutputParser
from typing import Any
from config import SYSTEM_MSG_TYPES
from data_io import images
from langchain_core.messages import HumanMessage
from utils.utils import ModelConfig

class TravelAgencyChatbot:
    def __init__(self):
        self.prompt = propmts.build_prompt()
        self.parser = StrOutputParser()

    def answer_invoke(
        self,
        message: Any,
        chat_history: list,
        model_config: ModelConfig,
        file_context: str = "",
    ):

        res = ""
        if isinstance(message, dict):
            text = (message.get("text") or "").strip()
            image_paths = message.get("files", list())
        else:
            text = str(message).strip()
            image_paths = list()

        history_messages = history.store_chat_history(chat_history)
        system_message = SYSTEM_MSG_TYPES.get(model_config.system_type, SYSTEM_MSG_TYPES["Basic(기본)"]).strip()

        if file_context and file_context.strip():
            system_message += "\n\nReference context from uploaded file:\n" + file_context

        if image_paths:
            parts = [
                {"type": "text", "text": text or "Plan the travel schedule based on the image what user uploaded."}
            ]
            for a_path in image_paths:
                url = images.image_to_url(a_path)
                if url:
                    parts.append({"type": "image_url", "image_url": {"url": url}})
            history_messages.append(HumanMessage(content=parts))

        model = openai_client.load_llm_model(model_config)

        chain = self.prompt | model | self.parser

        for chunk in chain.stream(
            {"system_message": system_message, "chat_history": history_messages, "user_input": message}
        ):
            res += chunk
            yield res
