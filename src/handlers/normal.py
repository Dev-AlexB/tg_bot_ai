from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from lexicon.lexicon import LEXICON_RU


router = Router()


@router.message(CommandStart())
async def process_start_command(message: Message):
    await message.answer(text=LEXICON_RU["/start"])


@router.message(Command(commands="help"))
async def process_help_command(message: Message):
    await message.answer(text=LEXICON_RU["/help"])


@router.message(F.text)
async def process_request(message: Message):
    request = message.text  # noqa
    # тут вызов функции с запросом к API LLM, передаем в нее request
    # тут запрос к базе с тем что вернула LLM
    await message.answer(
        text="Ответ по данным из базы"
    )  # todo: тут из базы должно вернуться число
