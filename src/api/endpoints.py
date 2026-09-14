import asyncio
from concurrent.futures import ThreadPoolExecutor

from deep_translator import GoogleTranslator as GT
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, HttpUrl
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.models import SavedSummary
from src.services.gemini import SummaryResponse, generate_ai_summary
from src.services.scraper import extract_article_content

router = APIRouter(prefix="/api/v1", tags=["Summarizer"])


class TranslationRequest(BaseModel):
    url: HttpUrl
    target_language: str


class SummaryRequest(BaseModel):
    url: HttpUrl


executor = ThreadPoolExecutor(max_workers=3)


def _execute_batch_translation(texts: list[str], target_lang: str) -> list[str]:
    """Executa a tradução de uma lista de textos em uma única requisição HTTP."""
    return GT(source="auto", target=target_lang).translate_batch(texts)


async def translate_batch_async(texts: list[str], target_lang: str) -> list[str]:
    """Executa a tradução em lote de forma assíncrona utilizando a ThreadPool."""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(
        executor, _execute_batch_translation, texts, target_lang
    )


@router.post(
    "/summarize",
    response_model=SummaryResponse,
    status_code=status.HTTP_200_OK,
    summary="Scrape and summarize a web article",
    description="Takes a URL, extracts core content, checks SQLite cache, and uses Gemini if not cached."
)
async def summarize_url(payload: SummaryRequest, db: AsyncSession = Depends(get_db)):
    url_str = str(payload.url)

    try:
        result = await db.execute(select(SavedSummary).where(SavedSummary.url == url_str))
        cached_summary = result.scalar_one_or_none()

        if cached_summary:
            return {
                "title": cached_summary.title,
                "summary": cached_summary.summary,
                "key_takeaways": cached_summary.key_takeaways,
                "estimated_reading_time": cached_summary.estimated_reading_time
            }

        clean_text = await extract_article_content(url_str)
        ai_analysis = await generate_ai_summary(clean_text)

        new_cache = SavedSummary(
            url=url_str,
            title=ai_analysis.title,
            summary=ai_analysis.summary,
            key_takeaways=ai_analysis.key_takeaways,
            estimated_reading_time=ai_analysis.estimated_reading_time
        )
        db.add(new_cache)
        await db.commit()

        return ai_analysis

    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(val_err)
        )


@router.post("/translate", status_code=status.HTTP_200_OK)
async def translate_cached_summary(payload: TranslationRequest, db: AsyncSession = Depends(get_db)):
    url_str = str(payload.url)

    result = await db.execute(select(SavedSummary).where(SavedSummary.url == url_str))
    cached = result.scalar_one_or_none()

    if not cached:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Este link ainda não foi sumarizado. Processe o link primeiro na rota principal."
        )

    try:
        all_texts = [cached.title, cached.summary] + list(cached.key_takeaways)

        translated_batch = await translate_batch_async(all_texts, payload.target_language)

        translated_title = translated_batch[0]
        translated_summary = translated_batch[1]
        translated_takeaways = translated_batch[2:]

        return {
            "title": translated_title,
            "summary": translated_summary,
            "key_takeaways": translated_takeaways,
            "estimated_reading_time": cached.estimated_reading_time
        }

    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao traduzir o conteúdo: {str(err)}"
        )
