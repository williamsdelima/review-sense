import httpx
from bs4 import BeautifulSoup
from fastapi import HTTPException


async def extract_article_content(url: str) -> str:
   headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
    }

   try:
      async with httpx.AsyncClient(timeout=10.0) as client:
         response = await client.get(url, headers=headers)

         if response.status_code != 200:
            raise HTTPException (
               status_code=400,
               detail=f'Failed to fetch the website. Status code: {response.status_code}'
            )
         soup = BeautifulSoup(response.text, 'html.parser')

         for element in soup(['script', 'style', 'nav', 'header', 'aside', 'form']):
            element.decompose()

      article_body = soup.find('article') or soup.find('main') or soup.find('body')

      if not article_body:
         raise HTTPException(status_code=422, detail='Could not extract readable text content from this URL.')
      text = article_body.get_text(separator=' ')
      clean_text = ' '.join(text.split())
      if len(clean_text) < 200:
         raise HTTPException(status_code=422, detail="The extracted content is too short be summarized.")

      return clean_text

   except httpx.RequestError as exc:
      raise HTTPException(status_code=503, detail=f'Network error while connecting to the URL: {str(exc)}')
