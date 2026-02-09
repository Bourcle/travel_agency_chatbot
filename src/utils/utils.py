from pydantic import BaseModel, Field


class ModelSettings(BaseModel):
    system_type: str = Field(default="기본")
    model_name: str = Field(default="gpt-4o-mini")
    temperature: float = Field(default=0.3, ge=0.0, le=1.0)
    top_p: float = Field(default=0.9, ge=0.0, le=1.0)
    presence_penalty: float = Field(default=0.3, ge=-2.0, le=2.0)
    frequency_penalty: float = Field(default=0.3, ge=-2.0, le=2.0)
