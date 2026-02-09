from langchain_core.messages import HumanMessage, AIMessage
from typing import Any


def store_chat_history(history: list[dict[str, str]]) -> list:
    """Store chat history from Gradio ChatInterface history between user and ai.
    Moreover, transfer it to Langchain messages

    Args:
        history (dict[tuple[str, str]]): The history from previous chat between user and ai

    Returns:
        list: Langchain messages
    """

    res: list[Any] = list()
    if not history:
        return res

    if isinstance(history[0], dict) and "role" in history[0]:
        for msg in history:
            if msg["role"] == "user":
                res.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                res.append(AIMessage(content=msg["content"]))
    else:
        for pair in history:
            if not pair or len(pair) < 2:
                continue
            user_msg, ai_msg = pair
            if isinstance(user_msg, str) and user_msg.strip():
                res.append(HumanMessage(content=user_msg))
            if isinstance(ai_msg, str) and ai_msg.strip():
                res.append(AIMessage(content=ai_msg))

    return res
