import logging

from aiogram import BaseMiddleware
from aiogram.types import Message


logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Message, data):
        log_data = {
            "user_id": event.from_user.id,
            "type": event.content_type,
        }
        if event.text:
            log_data["text"] = event.text[:100]
        logger.info("Получено сообщение: %s", log_data)
        return await handler(event, data)
