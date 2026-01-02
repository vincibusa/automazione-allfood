"""Gemini-based web search and scraping using Google Search grounding and URL context."""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import asyncio
from concurrent.futures import ThreadPoolExecutor

from google import genai
from google.genai import types
from config.settings import settings
from config.sources import SEARCH_QUERIES, ALL_SITES
from utils.retry import retry_api_call

logger = logging.getLogger(__name__)


class GeminiSearch:
    """Gemini-based web search and scraping using Google Search grounding."""
    
    def __init__(self):
        """Initialize Gemini client with Google Search tool."""
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model = settings.GEMINI_TEXT_MODEL
        
        # Configura Google Search grounding
        self.search_config = types.GenerateContentConfig(
            tools=[types.Tool(google_search=types.GoogleSearch())]
        )
        
        logger.info(f"Initialized Gemini search/scraper with model: {self.model}")
    
    @retry_api_call(max_attempts=3)
    def _search_single_query(
        self,
        query: str,
        days_back: int,
        limit: int,
        query_index: int,
        total_queries: int
    ) -> List[Dict[str, Any]]:
        """Search a single query (internal method for parallelization).
        
        Args:
            query: Search query
            days_back: Number of days to look back
            limit: Maximum number of results
            query_index: Index of this query (1-based)
            total_queries: Total number of queries
            
        Returns:
            List of search results
        """
        try:
            logger.info(f"   🔎 Query {query_index}/{total_queries}: '{query}'")
            logger.info(f"      📝 Creazione prompt per Gemini...")
            
            # Conta risultati prima della query
            results_before_query = []
            
            # Crea prompt che include il filtro temporale
            search_prompt = f"""Cerca notizie recenti (ultimi {days_back} giorni) su: {query} in Sicilia, 
focus su food, ristoranti, gastronomia siciliana.

Restituisci un JSON con i risultati trovati:
{{
  "results": [
    {{
      "url": "URL dell'articolo",
      "title": "Titolo",
      "snippet": "Breve descrizione"
    }}
  ]
}}

Massimo {limit} risultati. Solo notizie recenti e rilevanti."""
            
            logger.info(f"      📤 Invio richiesta a Gemini API...")
            logger.info(f"         - Modello: {self.model}")
            logger.info(f"         - Tool: Google Search")
            logger.info(f"         - Prompt length: {len(search_prompt)} caratteri")
            
            import time
            start_time = time.time()
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=[search_prompt],
                config=self.search_config
            )
            
            elapsed = time.time() - start_time
            logger.info(f"      ⏱️  Risposta ricevuta in {elapsed:.2f} secondi")
            
            # Estrai testo dalla risposta
            response_text = ""
            parts_count = 0
            for part in response.parts:
                if part.text:
                    response_text += part.text
                    parts_count += 1
            
            logger.info(f"      📥 Analisi risposta...")
            logger.info(f"         - Parti ricevute: {parts_count}")
            logger.info(f"         - Lunghezza testo: {len(response_text)} caratteri")
            
            query_results = []
            
            # Estrai grounding metadata (URLs trovati da Google Search)
            grounding_results = 0
            if hasattr(response, 'grounding_metadata') and response.grounding_metadata:
                logger.info(f"      🔗 Grounding metadata presente - estrazione risultati Google Search...")
                # Usa i risultati di grounding come fonte principale
                grounding = response.grounding_metadata
                
                if hasattr(grounding, 'grounding_chunks'):
                    chunks_count = len(grounding.grounding_chunks) if hasattr(grounding.grounding_chunks, '__len__') else 0
                    logger.info(f"         - Grounding chunks trovati: {chunks_count}")
                    
                    for chunk_idx, chunk in enumerate(grounding.grounding_chunks, 1):
                        if hasattr(chunk, 'web') and chunk.web:
                            web_result = chunk.web
                            url = getattr(web_result, 'uri', '')
                            title = getattr(web_result, 'title', '')
                            
                            query_results.append({
                                "url": url,
                                "title": title,
                                "snippet": getattr(web_result, 'snippet', ''),
                                "source": "gemini_search"
                            })
                            grounding_results += 1
                            
                            logger.info(f"         [{chunk_idx}] {title[:50]}...")
                            logger.info(f"            URL: {url}")
            
            # Se non ci sono grounding chunks, prova a parsare il JSON dalla risposta
            json_results = 0
            if grounding_results == 0 and response_text:
                logger.info(f"      📋 Nessun grounding metadata, tentativo parsing JSON dalla risposta...")
                try:
                    import json
                    # Prova a estrarre JSON dalla risposta
                    if "{" in response_text:
                        json_start = response_text.find("{")
                        json_end = response_text.rfind("}") + 1
                        json_str = response_text[json_start:json_end]
                        logger.info(f"         - JSON estratto: {len(json_str)} caratteri")
                        
                        parsed = json.loads(json_str)
                        
                        if "results" in parsed:
                            json_results = len(parsed["results"])
                            query_results.extend(parsed["results"])
                            logger.info(f"         - Risultati dal JSON: {json_results}")
                            for idx, res in enumerate(parsed["results"][:3], 1):
                                logger.info(f"            [{idx}] {res.get('title', 'N/A')[:50]}...")
                except Exception as e:
                    logger.warning(f"         ⚠️  Impossibile parsare JSON: {str(e)}")
            
            logger.info(f"      ✅ Query '{query}' completata:")
            logger.info(f"         - Risultati da Google Search: {grounding_results}")
            logger.info(f"         - Risultati da JSON: {json_results}")
            logger.info(f"         - Totale risultati: {len(query_results)}")
            logger.info("")
            
            return query_results
                    
        except Exception as e:
            logger.error(f"      ❌ Errore ricerca query '{query}': {str(e)}")
            logger.error(f"         Tipo errore: {type(e).__name__}")
            import traceback
            logger.debug(f"         Traceback: {traceback.format_exc()}")
            logger.info("")
            return []
    
    async def _search_query_async(
        self,
        query: str,
        days_back: int,
        limit: int,
        query_index: int,
        total_queries: int
    ) -> List[Dict[str, Any]]:
        """Async wrapper for single query search."""
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor(max_workers=1) as executor:
            return await loop.run_in_executor(
                executor,
                self._search_single_query,
                query,
                days_back,
                limit,
                query_index,
                total_queries
            )
    
    @retry_api_call(max_attempts=3)
    def search_food_news(
        self,
        days_back: int = 7,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Search for food news in Sicily using Gemini with Google Search (parallelized).
        
        Args:
            days_back: Number of days to look back (usato nel prompt)
            limit: Maximum number of results (approssimativo)
            
        Returns:
            List of search results with URL and snippet
        """
        logger.info(f"🔍 Ricerca notizie food (ultimi {days_back} giorni) con Gemini + Google Search")
        logger.info(f"   📊 Query da eseguire: {len(SEARCH_QUERIES)}")
        logger.info(f"   🤖 Modello: {self.model}")
        logger.info(f"   🔧 Configurazione: Google Search grounding attivato")
        logger.info(f"   ⚡ Esecuzione parallela delle query")
        logger.info("")
        
        async def search_all_queries_parallel():
            """Search all queries in parallel."""
            # Create tasks for all queries
            tasks = [
                self._search_query_async(
                    query,
                    days_back,
                    limit,
                    i+1,
                    len(SEARCH_QUERIES)
                )
                for i, query in enumerate(SEARCH_QUERIES)
            ]
            
            # Execute in parallel
            logger.info(f"⚡ Avvio ricerca parallela di {len(SEARCH_QUERIES)} query...")
            import time
            start_time = time.time()
            
            results_list = await asyncio.gather(*tasks, return_exceptions=True)
            
            elapsed = time.time() - start_time
            logger.info(f"⏱️  Tutte le query completate in {elapsed:.2f} secondi")
            logger.info("")
            
            # Flatten results
            all_results = []
            for i, result in enumerate(results_list):
                if isinstance(result, Exception):
                    logger.error(f"   ❌ Query {i+1} fallita: {type(result).__name__}")
                    continue
                if isinstance(result, list):
                    all_results.extend(result)
            
            return all_results
        
        # Run async search
        all_results = asyncio.run(search_all_queries_parallel())
        
        for i, query in enumerate(SEARCH_QUERIES, 1):
            try:
                logger.info(f"   🔎 Query {i}/{len(SEARCH_QUERIES)}: '{query}'")
                logger.info(f"      📝 Creazione prompt per Gemini...")
                
                # Conta risultati prima della query
                results_before_query = len(all_results)
                
                # Crea prompt che include il filtro temporale
                search_prompt = f"""Cerca notizie recenti (ultimi {days_back} giorni) su: {query} in Sicilia, 
focus su food, ristoranti, gastronomia siciliana.

Restituisci un JSON con i risultati trovati:
{{
  "results": [
    {{
      "url": "URL dell'articolo",
      "title": "Titolo",
      "snippet": "Breve descrizione"
    }}
  ]
}}

Massimo {limit} risultati. Solo notizie recenti e rilevanti."""
                
                logger.info(f"      📤 Invio richiesta a Gemini API...")
                logger.info(f"         - Modello: {self.model}")
                logger.info(f"         - Tool: Google Search")
                logger.info(f"         - Prompt length: {len(search_prompt)} caratteri")
                
                import time
                start_time = time.time()
                
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=[search_prompt],
                    config=self.search_config
                )
                
                elapsed = time.time() - start_time
                logger.info(f"      ⏱️  Risposta ricevuta in {elapsed:.2f} secondi")
                
                # Estrai testo dalla risposta
                response_text = ""
                parts_count = 0
                for part in response.parts:
                    if part.text:
                        response_text += part.text
                        parts_count += 1
                
                logger.info(f"      📥 Analisi risposta...")
                logger.info(f"         - Parti ricevute: {parts_count}")
                logger.info(f"         - Lunghezza testo: {len(response_text)} caratteri")
                
                # Estrai grounding metadata (URLs trovati da Google Search)
                grounding_results = 0
                if hasattr(response, 'grounding_metadata') and response.grounding_metadata:
                    logger.info(f"      🔗 Grounding metadata presente - estrazione risultati Google Search...")
                    # Usa i risultati di grounding come fonte principale
                    grounding = response.grounding_metadata
                    
                    if hasattr(grounding, 'grounding_chunks'):
                        chunks_count = len(grounding.grounding_chunks) if hasattr(grounding.grounding_chunks, '__len__') else 0
                        logger.info(f"         - Grounding chunks trovati: {chunks_count}")
                        
                        for chunk_idx, chunk in enumerate(grounding.grounding_chunks, 1):
                            if hasattr(chunk, 'web') and chunk.web:
                                web_result = chunk.web
                                url = getattr(web_result, 'uri', '')
                                title = getattr(web_result, 'title', '')
                                
                                all_results.append({
                                    "url": url,
                                    "title": title,
                                    "snippet": getattr(web_result, 'snippet', ''),
                                    "source": "gemini_search"
                                })
                                grounding_results += 1
                                
                                logger.info(f"         [{chunk_idx}] {title[:50]}...")
                                logger.info(f"            URL: {url}")
                
                # Se non ci sono grounding chunks, prova a parsare il JSON dalla risposta
                json_results = 0
                if grounding_results == 0 and response_text:
                    logger.info(f"      📋 Nessun grounding metadata, tentativo parsing JSON dalla risposta...")
                    try:
                        import json
                        # Prova a estrarre JSON dalla risposta
                        if "{" in response_text:
                            json_start = response_text.find("{")
                            json_end = response_text.rfind("}") + 1
                            json_str = response_text[json_start:json_end]
                            logger.info(f"         - JSON estratto: {len(json_str)} caratteri")
                            
                            parsed = json.loads(json_str)
                            
                            if "results" in parsed:
                                json_results = len(parsed["results"])
                                all_results.extend(parsed["results"])
                                logger.info(f"         - Risultati dal JSON: {json_results}")
                                for idx, res in enumerate(parsed["results"][:3], 1):
                                    logger.info(f"            [{idx}] {res.get('title', 'N/A')[:50]}...")
                    except Exception as e:
                        logger.warning(f"         ⚠️  Impossibile parsare JSON: {str(e)}")
                
                # Conta risultati aggiunti in questa query
                results_after_query = len(all_results)
                new_results = results_after_query - results_before_query
                
                logger.info(f"      ✅ Query '{query}' completata:")
                logger.info(f"         - Risultati da Google Search: {grounding_results}")
                logger.info(f"         - Risultati da JSON: {json_results}")
                logger.info(f"         - Nuovi risultati aggiunti: {new_results}")
                logger.info(f"         - Totale risultati accumulati: {results_after_query}")
                logger.info("")
                    
            except Exception as e:
                logger.error(f"      ❌ Errore ricerca query '{query}': {str(e)}")
                logger.error(f"         Tipo errore: {type(e).__name__}")
                import traceback
                logger.debug(f"         Traceback: {traceback.format_exc()}")
                logger.info("")
                continue
                    
            except Exception as e:
                logger.error(f"   ❌ Errore ricerca query '{query}': {str(e)}")
                continue
        
        # Remove duplicates based on URL
        logger.info("   🔄 Rimozione duplicati...")
        seen_urls = set()
        unique_results = []
        duplicates = 0
        
        for result in all_results:
            url = result.get("url", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_results.append(result)
            else:
                duplicates += 1
        
        logger.info(f"   📊 Risultati finali:")
        logger.info(f"      - Totali raccolti: {len(all_results)}")
        logger.info(f"      - Duplicati rimossi: {duplicates}")
        logger.info(f"      - Risultati unici: {len(unique_results)}")
        
        if unique_results:
            logger.info(f"   📋 Esempi risultati trovati:")
            for i, result in enumerate(unique_results[:3], 1):
                logger.info(f"      {i}. {result.get('title', 'N/A')[:60]}...")
                logger.info(f"         URL: {result.get('url', 'N/A')[:80]}")
        
        return unique_results
    
    @retry_api_call(max_attempts=3)
    def scrape_url(self, url: str) -> Optional[Dict[str, Any]]:
        """Scrape a single URL using Gemini URL context tool.
        
        Args:
            url: URL to scrape
            
        Returns:
            Scraped content or None if error
        """
        try:
            logger.info(f"      🔗 Scraping: {url}")
            logger.info(f"         🤖 Modello: {self.model}")
            logger.info(f"         🔧 Tool: URL Context")
            
            # Gemini può leggere URL direttamente usando URL context tool
            prompt = f"""Leggi e analizza il contenuto di questa pagina web: {url}

Estrai in formato markdown:
- Titolo dell'articolo
- Contenuto principale (focus su food/gastronomia se presente)
- Informazioni rilevanti per un giornale food siciliano

Restituisci il contenuto completo in formato markdown pulito."""
            
            logger.info(f"         📝 Prompt creato: {len(prompt)} caratteri")
            
            # Usa URL context tool per leggere la pagina
            scrape_config = types.GenerateContentConfig(
                tools=[types.Tool(url_context=types.UrlContext())]
            )
            
            logger.info(f"         📤 Invio richiesta a Gemini API con URL Context...")
            import time
            start_time = time.time()
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=[prompt],
                config=scrape_config
            )
            
            elapsed = time.time() - start_time
            logger.info(f"         ⏱️  Risposta ricevuta in {elapsed:.2f} secondi")
            
            # Estrai contenuto dalla risposta
            content_text = ""
            parts_count = 0
            for part in response.parts:
                if part.text:
                    content_text += part.text
                    parts_count += 1
            
            logger.info(f"         📥 Analisi risposta...")
            logger.info(f"            - Parti ricevute: {parts_count}")
            logger.info(f"            - Lunghezza contenuto: {len(content_text)} caratteri")
            
            if content_text:
                # Estrai titolo (prima riga o da metadata)
                lines = content_text.split('\n')
                title = lines[0].replace('#', '').strip() if lines else url
                word_count = len(content_text.split())
                
                logger.info(f"         📊 Contenuto estratto:")
                logger.info(f"            - Titolo: {title[:60]}...")
                logger.info(f"            - Parole: {word_count}")
                logger.info(f"            - Righe: {len(lines)}")
                
                # Verifica metadata URL context
                url_metadata = None
                if hasattr(response, 'candidates') and response.candidates:
                    candidate = response.candidates[0]
                    if hasattr(candidate, 'url_context_metadata'):
                        url_metadata = candidate.url_context_metadata
                        logger.info(f"         ✅ URL Context metadata presente")
                    else:
                        logger.info(f"         ℹ️  Nessun URL Context metadata nella risposta")
                
                return {
                    "url": url,
                    "content": content_text,
                    "title": title,
                    "success": True,
                    "metadata": url_metadata
                }
            else:
                logger.warning(f"         ⚠️  Nessun contenuto estratto dalla risposta")
                return None
                
        except Exception as e:
            logger.error(f"         ❌ Errore scraping: {str(e)}")
            logger.error(f"            Tipo errore: {type(e).__name__}")
            import traceback
            logger.debug(f"            Traceback: {traceback.format_exc()}")
            return None
    
    async def scrape_url_async(self, url: str, site_name: str = "") -> Optional[Dict[str, Any]]:
        """Async wrapper for scrape_url with timeout.
        
        Args:
            url: URL to scrape
            site_name: Name of the site (for logging)
            
        Returns:
            Scraped content or None if error
        """
        try:
            logger.info(f"   🕷️  [{site_name}] Avvio scraping...")
            # Usa ThreadPoolExecutor per eseguire il metodo sincrono in parallelo
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor(max_workers=1) as executor:
                # Timeout di 60 secondi per sito
                result = await asyncio.wait_for(
                    loop.run_in_executor(executor, self.scrape_url, url),
                    timeout=60.0
                )
                if result and site_name:
                    logger.info(f"   ✅ [{site_name}] Scraping completato con successo")
                elif site_name:
                    logger.warning(f"   ⚠️  [{site_name}] Scraping completato ma nessun contenuto")
                return result
        except asyncio.TimeoutError:
            logger.warning(f"   ⏱️  [{site_name}] Timeout dopo 60 secondi")
            logger.warning(f"      URL: {url}")
            return None
        except Exception as e:
            logger.error(f"   ❌ [{site_name}] Errore durante scraping: {str(e)}")
            logger.error(f"      URL: {url}")
            return None
    
    async def scrape_sites_parallel(
        self, 
        max_concurrent: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Scrape all monitored sites in parallel using Gemini with concurrency control.
        
        Args:
            max_concurrent: Maximum number of concurrent scraping operations (default from settings)
            
        Returns:
            List of scraped content from all sites
        """
        if max_concurrent is None:
            max_concurrent = settings.MAX_CONCURRENT_SCRAPES
        
        logger.info(f"🚀 Avvio scraping parallelo di {len(ALL_SITES)} siti con Gemini")
        logger.info(f"📊 Configurazione:")
        logger.info(f"   - Concorrenza massima: {max_concurrent} richieste simultanee")
        logger.info(f"   - Timeout per sito: 60 secondi")
        logger.info(f"   - Modello: {self.model}")
        logger.info(f"   - Tool: URL Context")
        logger.info("")
        logger.info(f"📋 Siti da processare:")
        for i, site in enumerate(ALL_SITES, 1):
            logger.info(f"   {i}. {site['name']} ({site['type']}) - {site['url']}")
        logger.info("")
        
        # Crea semaforo per limitare la concorrenza
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def scrape_with_semaphore(site: Dict[str, Any]) -> Optional[Dict[str, Any]]:
            """Scrape con controllo concorrenza."""
            async with semaphore:
                logger.info(f"   🔓 Slot disponibile - avvio scraping {site['name']}")
                result = await self.scrape_url_async(site["url"], site["name"])
                if result:
                    result["site_name"] = site["name"]
                    result["site_type"] = site["type"]
                logger.info(f"   🔒 Slot rilasciato - {site['name']} completato")
                return result
        
        # Crea tasks per tutti i siti
        logger.info(f"📦 Creazione {len(ALL_SITES)} task per scraping parallelo...")
        tasks = [scrape_with_semaphore(site) for site in ALL_SITES]
        
        # Esegui in parallelo con gestione errori
        logger.info(f"⚡ Esecuzione scraping parallelo (max {max_concurrent} simultanei)...")
        import time
        start_time = time.time()
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        elapsed = time.time() - start_time
        logger.info(f"⏱️  Tutti i task completati in {elapsed:.2f} secondi")
        logger.info("")
        
        # Processa risultati
        logger.info(f"📊 Analisi risultati...")
        scraped_content = []
        successful = 0
        failed = 0
        timeout_count = 0
        
        for i, result in enumerate(results):
            site = ALL_SITES[i]
            
            if isinstance(result, Exception):
                logger.error(f"   ❌ [{site['name']}] Eccezione: {type(result).__name__}")
                logger.error(f"      Messaggio: {str(result)}")
                failed += 1
                continue
            
            if result:
                content_len = len(result.get('content', ''))
                word_count = len(result.get('content', '').split())
                scraped_content.append(result)
                successful += 1
                logger.info(f"   ✅ [{site['name']}] Successo:")
                logger.info(f"      - Contenuto: {content_len} caratteri, {word_count} parole")
                logger.info(f"      - Titolo: {result.get('title', 'N/A')[:60]}...")
            else:
                logger.warning(f"   ⚠️  [{site['name']}] Nessun contenuto estratto")
                failed += 1
        
        logger.info("")
        logger.info(f"📊 Riepilogo scraping:")
        logger.info(f"   ✅ Successi: {successful}/{len(ALL_SITES)}")
        logger.info(f"   ❌ Falliti: {failed}/{len(ALL_SITES)}")
        logger.info(f"   ⏱️  Timeout: {timeout_count}")
        logger.info(f"   📝 Contenuti totali estratti: {sum(len(r.get('content', '')) for r in scraped_content)} caratteri")
        
        return scraped_content
    
    def scrape_sites_sync(self) -> List[Dict[str, Any]]:
        """Synchronous wrapper for scrape_sites_parallel.
        
        Returns:
            List of scraped content from all sites
        """
        return asyncio.run(self.scrape_sites_parallel())

