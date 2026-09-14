import asyncio
from concurrent.futures import ThreadPoolExecutor

from deep_translator import GoogleTranslator as GT

executor = ThreadPoolExecutor(max_workers=3)

def translate_batch_texts(texts: list[str], target_lang: str) -> list[str]:
    """Traduz uma lista de textos em uma única requisição HTTP."""
    return GT(source="auto", target=target_lang).translate_batch(texts)

async def translate_batch_async(texts: list[str], target_lang: str) -> list[str]:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(executor, translate_batch_texts, texts, target_lang)
