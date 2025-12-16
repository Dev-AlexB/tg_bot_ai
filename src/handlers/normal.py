from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from errors.errors import SqlExecutionError
from lexicon.lexicon import LEXICON_RU
from services.llm.llm import OllamaLLMService
from services.llm.query_processor import QueryProcessor


router = Router()


@router.message(CommandStart())
async def process_start_command(message: Message):
    await message.answer(LEXICON_RU["/start"])


@router.message(Command(commands="help"))
async def process_help_command(message: Message):
    await message.answer(LEXICON_RU["/help"])


@router.message(F.text)
async def process_request(message: Message):
    processor = QueryProcessor(OllamaLLMService())

    try:
        value = await processor.process(message.text)
        await message.answer(value)

    except SqlExecutionError:
        await message.answer("Ошибка при выполнении запроса к базе данных.")

    except Exception:
        await message.answer(
            "Не удалось обработать запрос. Попробуйте переформулировать."
        )
