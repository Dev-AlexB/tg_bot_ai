import asyncio
import logging

import httpx

from config import settings
from services.llm.prompt import SYSTEM_PROMPT
from services.llm.schema import LLMResultModel


logger = logging.getLogger(__name__)


class OllamaLLMService:
    def __init__(self, model: str = "qwen2.5:3b", base_url: str | None = None):
        self.model = model
        self.base_url = base_url or settings.ollama.url
        self.url = f"{self.base_url}/api/generate"

    async def warmup(self):
        """Прогрев модели коротким запросом"""
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                resp = await client.post(
                    self.url,
                    json={
                        "model": self.model,
                        "prompt": "SELECT 1",
                        "stream": False,
                        "options": {"temperature": 0.0, "num_predict": 50},
                    },
                )
                logger.info("LLM warmup done")
                resp.raise_for_status()
        except Exception as e:
            logger.warning("LLM warmup failed, continue: %s", e)

    async def interpret(
        self, question: str, retries: int = 3, backoff: float = 2.0
    ) -> LLMResultModel:
        full_prompt = SYSTEM_PROMPT + f"\nВопрос пользователя: {question}"
        attempt = 0
        while attempt < retries:
            attempt += 1
            try:
                async with httpx.AsyncClient(timeout=120) as client:
                    resp = await client.post(
                        self.url,
                        json={
                            "model": self.model,
                            "prompt": full_prompt,
                            "stream": False,
                            "options": {
                                "temperature": 0.0,
                                "num_predict": 200,
                            },
                        },
                    )
                    resp.raise_for_status()
                    json_str = resp.json()["response"]
                    logger.info(f"Got LLM response {json_str}")
                    return LLMResultModel.model_validate_json(json_str)

            except (
                httpx.HTTPStatusError,
                httpx.RequestError,
                httpx.TimeoutException,
            ) as e:
                logger.warning(f"[Attempt {attempt}] HTTP/network error: {e}")
            except Exception as e:
                logger.warning(
                    f"[Attempt {attempt}] Invalid LLM response: {e}"
                )

            if attempt < retries:
                sleep_time = backoff * attempt
                logger.info(f"Retrying after {sleep_time:.1f}s...")
                await asyncio.sleep(sleep_time)

        raise RuntimeError(
            f"LLM can't return valid result after {retries} retries"
        )
