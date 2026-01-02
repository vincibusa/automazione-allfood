"""Google Gemini API client for text generation and analysis."""

import json
import logging
from typing import List, Dict, Any, Optional

from google import genai
from google.genai import types
from config.settings import settings
from models.schemas import TopicsResponse, Topic
from utils.retry import retry_api_call

logger = logging.getLogger(__name__)


class GeminiClient:
    """Gemini API client for text generation."""
    
    def __init__(self):
        """Initialize Gemini client."""
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model = settings.GEMINI_TEXT_MODEL
        logger.info(f"Initialized Gemini client with model: {self.model}")
    
    @retry_api_call(max_attempts=3)
    def analyze_topics(
        self,
        search_results: List[Dict[str, Any]],
        scraped_content: List[Dict[str, Any]]
    ) -> List[Topic]:
        """Analyze content and select 3-5 interesting topics.
        
        Args:
            search_results: Results from Gemini search
            scraped_content: Scraped content from monitored sites
            
        Returns:
            List of selected topics
        """
        logger.info("Analyzing content to select topics")
        
        # Prepare context
        context = self._prepare_analysis_context(search_results, scraped_content)
        
        prompt = f"""Analizza le seguenti notizie food dalla Sicilia e identifica 3-5 topic interessanti per il giornale AllFoodSicily.

Criteri di selezione:
- Evita duplicati con articoli già pubblicati sui competitor
- Focus su: eventi, aperture ristoranti, ricette tradizionali, chef siciliani, prodotti tipici
- Seleziona solo notizie con valore editoriale e interesse per il pubblico
- Priorità a notizie recenti e rilevanti

Contenuti da analizzare:

{context}

Output richiesto (solo JSON valido, nessun testo aggiuntivo):
{{
  "topics": [
    {{
      "titolo": "Titolo dell'articolo proposto",
      "angolo": "Angolo editoriale (es: evento, apertura, ricetta, chef, prodotto)",
      "fonti": ["url1", "url2"],
      "keywords": ["keyword1", "keyword2", "keyword3"]
    }}
  ]
}}

Importante: Restituisci SOLO il JSON, senza markdown, senza spiegazioni."""
        
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=[prompt],
                config=types.GenerateContentConfig(
                    temperature=0.7,
                    max_output_tokens=2000
                )
            )
            
            # Extract text from response
            response_text = ""
            for part in response.parts:
                if part.text:
                    response_text += part.text
            
            # Parse JSON response
            # Try to extract JSON if wrapped in markdown
            response_text = response_text.strip()
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            topics_data = json.loads(response_text)
            topics_response = TopicsResponse(**topics_data)
            
            logger.info(f"Selected {len(topics_response.topics)} topics")
            return topics_response.topics
            
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON response: {str(e)}")
            logger.debug(f"Response text: {response_text}")
            raise
        except Exception as e:
            logger.error(f"Error analyzing topics: {str(e)}")
            raise
    
    def _prepare_analysis_context(
        self,
        search_results: List[Dict[str, Any]],
        scraped_content: List[Dict[str, Any]]
    ) -> str:
        """Prepare context string for analysis.
        
        Args:
            search_results: Search results
            scraped_content: Scraped content
            
        Returns:
            Formatted context string
        """
        context_parts = []
        
        # Add search results
        if search_results:
            context_parts.append("=== RISULTATI RICERCA ===\n")
            for i, result in enumerate(search_results[:10], 1):  # Limit to 10
                context_parts.append(
                    f"{i}. {result.get('title', 'N/A')}\n"
                    f"   URL: {result.get('url', '')}\n"
                    f"   Snippet: {result.get('snippet', '')}\n"
                )
        
        # Add scraped content
        if scraped_content:
            context_parts.append("\n=== CONTENUTI SCRAPED ===\n")
            for i, content in enumerate(scraped_content[:10], 1):  # Limit to 10
                context_parts.append(
                    f"{i}. {content.get('title', 'N/A')} ({content.get('site_name', 'Unknown')})\n"
                    f"   URL: {content.get('url', '')}\n"
                    f"   Contenuto: {content.get('content', '')[:500]}...\n"
                )
        
        return "\n".join(context_parts)
    
    @retry_api_call(max_attempts=3)
    def generate_article(self, topic: Topic) -> str:
        """Generate article content for a topic.
        
        Args:
            topic: Topic to write about
            
        Returns:
            Generated article in HTML/Markdown format
        """
        logger.info(f"Generating article for topic: {topic.titolo}")
        
        prompt = f"""Scrivi una bozza di articolo per AllFoodSicily sul seguente topic.

Titolo: {topic.titolo}
Angolo editoriale: {topic.angolo}
Keywords: {', '.join(topic.keywords)}
Fonti: {', '.join(topic.fonti)}

Requisiti dell'articolo:
- Tono: professionale ma accessibile, adatto a un pubblico appassionato di food
- Lunghezza: 500-800 parole
- Struttura: introduzione accattivante, corpo informativo con dettagli, conclusione con riflessione
- Cita le fonti originali quando appropriato
- Ottimizzato SEO per keywords siciliane e gastronomiche
- Formato: Markdown con titoli, paragrafi, e formattazione appropriata

Scrivi l'articolo completo in formato Markdown."""
        
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=[prompt],
                config=types.GenerateContentConfig(
                    temperature=0.8,
                    max_output_tokens=3000
                )
            )
            
            # Extract article text
            article_text = ""
            for part in response.parts:
                if part.text:
                    article_text += part.text
            
            # Count words (approximate)
            word_count = len(article_text.split())
            logger.info(f"Generated article with ~{word_count} words")
            
            return article_text
            
        except Exception as e:
            logger.error(f"Error generating article: {str(e)}")
            raise
    
    def generate_image_prompt(self, topic: Topic, article_content: str) -> str:
        """Generate a prompt for image generation based on topic and article.
        
        Args:
            topic: Article topic
            article_content: Generated article content
            
        Returns:
            Image generation prompt
        """
        # Extract key elements from article (first 500 chars)
        article_preview = article_content[:500]
        
        prompt = f"""Crea un prompt dettagliato per generare un'immagine professionale di food photography per questo articolo.

Titolo articolo: {topic.titolo}
Contenuto (anteprima): {article_preview}

Il prompt deve:
- Descrivere una fotografia professionale di food
- Essere specifico sul soggetto (piatto, ingrediente, o scena culinaria siciliana)
- Includere dettagli su stile fotografico, illuminazione, composizione
- Evocare l'ambientazione siciliana quando appropriato
- Essere adatto per un articolo di giornale food

Restituisci SOLO il prompt per l'immagine, senza spiegazioni aggiuntive."""
        
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=[prompt],
                config=types.GenerateContentConfig(
                    temperature=0.7,
                    max_output_tokens=500
                )
            )
            
            image_prompt = ""
            for part in response.parts:
                if part.text:
                    image_prompt += part.text
            
            return image_prompt.strip()
            
        except Exception as e:
            logger.error(f"Error generating image prompt: {str(e)}")
            # Fallback to simple prompt
            return f"Professional food photography of {topic.titolo}, Sicilian cuisine, high quality, magazine style"

