import logging

from aiogram import BaseMiddleware
from aiogram.types import Message


logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Message, data):
        logger.info(
            "\nMessage from user: %s, %s, message text:\n%s\n",
            event.from_user.id,
            event.content_type,
            event.text,
        )
        return await handler(event, data)
