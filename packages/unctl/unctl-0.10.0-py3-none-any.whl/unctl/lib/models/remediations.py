from dataclasses import field
from pydantic import BaseModel

from unctl.lib.checks.check_report import CheckReport
from unctl.lib.llm.session import LLMSessionKeeper


class FailureGroup(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    id: str
    title: str
    summary: str
    objects: list[CheckReport] = field(default_factory=list)
    session: LLMSessionKeeper | None

    @property
    def failed_count(self):
        return len(self.objects)

    def contains_object(self, object: str):
        return any(item for item in self.objects if item.unique_name == object)
