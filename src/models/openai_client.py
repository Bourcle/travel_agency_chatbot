from langchain_openai import ChatOpenAI
from utils.utils import ModelConfig


def load_llm_model(cfg: ModelConfig) -> ChatOpenAI:
    """Load llm model as set by config

    Args:
        cfg (ModelConfig): A model config

    Returns:
        ChatOpenAI: LLM model that is used in chat bot
    """

    res = ChatOpenAI(
        model=cfg.model_name,
        temperature=cfg.temperature,
        top_p=cfg.top_p,
        streaming=True,
        model_kwargs={"presence_penalty": cfg.presence_penalty, "frequency_penalty": cfg.frequency_penalty},
    )

    return res
