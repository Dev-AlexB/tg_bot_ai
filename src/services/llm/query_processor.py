import logging

from sqlalchemy import text

from db.database import async_session
from errors.errors import (
    InvalidSqlResultError,
    LLMError,
    ResponseValidationError,
    SqlExecutionError,
    SqlValidationError,
)
from services.llm.llm import OllamaLLMService
from services.llm.schema import LLMResultModel
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
            json_str: str = await self.llm.interpret(question)
        except Exception as e:
            logger.error(
                "LLM error | question=%s | error=%s",
                question,
                e,
            )
            raise LLMError(e)

        try:
            llm_result = LLMResultModel.model_validate_json(json_str)
        except Exception as e:
            logger.error(
                "LLM response validation error | question=%s | error=%s",
                question,
                e,
            )
            raise ResponseValidationError(e)

        if llm_result.status != "ok":
            raise LLMError(llm_result.reason or "LLM cannot generate SQL")

        self.validator.validate(llm_result.sql)

        value = await self.execute_scalar(llm_result.sql)

        if not isinstance(value, (int, float)):
            raise InvalidSqlResultError(
                f"Expected number, got {type(value).__name__}"
            )

        logger.info(
            "SQL executed successfully | question=%s | SQL=%s | value=%s",
            question,
            llm_result.sql,
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
                    question,
                    e,
                )
            except ResponseValidationError as e:
                last_error = e
                comment = (
                    "\nПрошлый ответ был невалидным JSON. "
                    "Формат ответа должен быть валидным JSON."
                )
                logger.warning(
                    "[Attempt %d] Invalid JSON in LLM output | question=%s | error=%s",
                    attempt,
                    question,
                    e,
                )

        logger.error(
            "All retries exhausted | question=%s | error=%s",
            question,
            last_error,
        )
        raise last_error
