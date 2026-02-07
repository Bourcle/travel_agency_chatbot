from chat_stream_core import propmts, history
from models import openai_client
from langchain_core.output_parsers import StrOutputParser
from typing import Any
from config import SYSTEM_MSG_TYPES
from data_io import images
from langchain_core.messages import HumanMessage


class TravelAgencyChatbot:
    def __init__(self):
        self.prompt = propmts.build_prompt()
        self.parser = StrOutputParser()

    def answer_invoke(
        self,
        message: Any,
        chat_history: list,
        system_type: str,
        model_name: str = "gpt-4o-mini",
        temperature: float = 0.3,
        top_p: float = 0.9,
        presence_penalty: float = 0.3,
        frequence_penalty: float = 0.3,
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
        system_message = SYSTEM_MSG_TYPES.get(system_type, SYSTEM_MSG_TYPES["기본"]).strip()

        if file_context and file_context.strip():
            system_message += "\n\nReference context from uploaded file:\n" + file_context

        if image_paths:
            parts = [
                {"type": "text", "text": text or "Plan the travel schedule based on the image what user uploaded."}
            ]
            for a_path in image_paths:
                url = images.image_to_url(a_path)
                if url:
                    parts.append({"type": "image_url", "imgae_url": {"url": url}})
            history_messages.append(HumanMessage(content=parts))

        cfg = openai_client.ModelConfig(
            model=model_name,
            temperature=temperature,
            top_p=top_p,
            presence_penalty=presence_penalty,
            frequency_penalty=frequence_penalty,
        )
        model = openai_client.load_llm_model(cfg)

        chain = self.prompt | model | self.parser

        for chunk in chain.stream(
            {"system_message": system_message, "chat_history": history_messages, "user_input": message}
        ):
            res += chunk
            yield res
