from aiogram import Router
from aiogram.types import Message

from lexicon.lexicon import LEXICON_RU


router = Router()


@router.message()
async def process_other(message: Message):
    await message.reply(text=LEXICON_RU["other"])
