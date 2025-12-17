import logging

from sqlalchemy import text

from db.database import async_session
from errors.errors import (
    InvalidSqlResultError,
    LLMError,
    SqlExecutionError,
    SqlValidationError,
)
from services.llm.llm import OllamaLLMService
from services.llm.sql_validator import SqlValidator


logger = logging.getLogger(__name__)


class QueryProcessor:
    def __init__(self, llm_service: OllamaLLMService):
        self.llm = llm_service
        self.validator = SqlValidator()

    async def execute_scalar(self, sql: str) -> int:
        try:
            async with async_session() as session:
                result = await session.execute(text(sql))
                return result.scalar_one() or 0
        except Exception as e:
            raise SqlExecutionError(e) from e

    async def _process_once(self, question: str) -> str:
        try:
            llm_result: str = await self.llm.interpret(question)
        except Exception as e:
            logger.error(
                "LLM error | question=%s | error=%s",
                question,
                e,
            )
            raise LLMError(e)

        self.validator.validate(llm_result)

        value = await self.execute_scalar(llm_result)

        if not isinstance(value, (int, float)):
            raise InvalidSqlResultError(
                f"Expected number, got {type(value).__name__}"
            )

        logger.info(
            "SQL executed successfully | question=%s | SQL=%s | value=%s",
            question,
            llm_result,
            value,
        )

        return str(value)

    async def process(self, question: str) -> str:
        last_error = None
        comment = ""
        for attempt in range(1, 4):
            try:
                return await self._process_once(question + comment)
            except (SqlValidationError, InvalidSqlResultError) as e:
                last_error = e
                comment = (
                    "\nПредыдущий твой ответ был некорректным. "
                    "Попробуй сгенерировать новый SQL."
                )
                logger.warning(
                    "[Attempt %d] Invalid SQL in LLM output | question=%s | error=%s",
                    attempt,
                    question + comment,
                    e,
                )

        logger.error(
            "All retries exhausted | question=%s | error=%s",
            question + comment,
            last_error,
        )
        raise last_error
