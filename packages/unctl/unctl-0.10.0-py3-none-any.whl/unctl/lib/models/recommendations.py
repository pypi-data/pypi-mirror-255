from dataclasses import field

from pydantic import BaseModel


class LLMRecommendation(BaseModel):
    """Model which reflects recommendation formed from llm response"""

    summary: str = ""
    fixes: list[str] = field(default_factory=list)
    objects: list[str] = field(default_factory=list)
    diagnostics: list[str] = field(default_factory=list)


class GroupLLMRecommendation(BaseModel):
    title: str = ""
    summary: str = ""
    objects: list[str] = field(default_factory=list)
