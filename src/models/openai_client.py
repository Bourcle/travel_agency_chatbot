from langchain_openai import ChatOpenAI
from dataclasses import dataclass


@dataclass
class ModelConfig:
    model: str
    temperature: float = 0.3
    top_p: float = 0.9
    presence_penalty: float = 0.3
    frequency_penalty: float = 0.2


def load_llm_model(cfg: ModelConfig) -> ChatOpenAI:
    """Load llm model as set by config

    Args:
        cfg (ModelConfig): A model config

    Returns:
        ChatOpenAI: LLM model that is used in chat bot
    """

    res = ChatOpenAI(
        model=cfg.model,
        temperature=cfg.temperature,
        top_p=cfg.top_p,
        streaming=True,
        model_kwargs={"presence_penalty": cfg.presence_penalty, "frequency_penalty": cfg.frequency_penalty},
    )

    return res
