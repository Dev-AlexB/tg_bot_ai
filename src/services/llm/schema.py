from typing import Literal

from pydantic import BaseModel


class LLMResultModel(BaseModel):
    status: Literal["ok", "cannot_answer", "invalid_question"]
    sql: str | None
    reason: str | None
