from google import genai
from google.genai import types
from pydantic import BaseModel, Field

from src.config.settings import settings


class SummaryResponse(BaseModel):
    title: str = Field(description="The clear and compelling headline of the article.")
    summary: str = Field(description="An executive summary consisting of 2 to 3 detailed paragraphs.")
    key_takeaways: list[str] = Field(description="An array containing up to 5 bullet points of the most crucial insights.")
    estimated_reading_time: str = Field(description="Estimated reading time of the original text (e.g., '5 min read').")

client = genai.Client(api_key=settings.gemini_api_key)

async def generate_ai_summary(article_text: str) -> SummaryResponse:
    prompt = f"""
    You are an enthusiastic researcher.
    Analyze the web content extracted below and draft a professional, highly accurate summary using simple language.
    Source text:
    {article_text}
    """

    try:

        response = await client.aio.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=SummaryResponse,
                temperature=0.3,
            ),
        )

        parsed_response = SummaryResponse.model_validate_json(response.text)
        return parsed_response

    except Exception as e:
        raise ValueError(f"Gemini API or Validation Error: {str(e)}")
