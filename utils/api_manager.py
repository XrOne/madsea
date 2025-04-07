#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module de gestion centralisée des appels API externes.
"""

import asyncio
import logging
import time
import aiohttp

logger = logging.getLogger(__name__)

class APIManager:
    """Gère les appels aux différentes API externes."""

    def __init__(self, config):
        """
        Initialise le gestionnaire d'API.

        Args:
            config (dict): Dictionnaire de configuration contenant les clés API et autres paramètres.
        """
        self.config = config
        self.api_keys = config.get("api_keys", {})
        self.rate_limits = {}  # Ex: {"openai": {"limit": 10, "period": 60, "last_call": 0, "count": 0}}
        self.session = None # aiohttp.ClientSession

    async def _get_session(self):
        """Crée ou retourne la session aiohttp."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    async def _rate_limit(self, api_name):
        """Applique un rate limiting simple."""
        if api_name in self.rate_limits:
            limit_info = self.rate_limits[api_name]
            now = time.time()
            elapsed = now - limit_info.get("last_call", 0)

            if elapsed < limit_info["period"]:
                if limit_info.get("count", 0) >= limit_info["limit"]:
                    wait_time = limit_info["period"] - elapsed
                    logger.warning(f"Rate limit reached for {api_name}. Waiting {wait_time:.2f} seconds.")
                    await asyncio.sleep(wait_time)
                    limit_info["count"] = 0 # Reset count after waiting
                    limit_info["last_call"] = time.time() # Update last_call after waiting
                else:
                     limit_info["count"] = limit_info.get("count", 0) + 1
            else:
                # Reset count if period has passed
                limit_info["count"] = 1
                limit_info["last_call"] = now
        # Update the rate limit info, adding api if not exists
        self.rate_limits[api_name] = limit_info if api_name in self.rate_limits else {"last_call": time.time(), "count": 1}


    def register_api(self, name, api_key=None, endpoint=None, rate_limit=None):
        """
        Enregistre une nouvelle API ou met à jour une existante.

        Args:
            name (str): Nom de l'API (ex: "openai", "gemini").
            api_key (str, optional): Clé API. Si None, essaie de la récupérer depuis la config.
            endpoint (str, optional): URL de base de l'API.
            rate_limit (dict, optional): Dictionnaire de configuration du rate limiting
                                         (ex: {"limit": 10, "period": 60}).
        """
        if api_key:
            self.api_keys[name] = api_key
        elif name not in self.api_keys:
             self.api_keys[name] = self.config.get("api_keys", {}).get(name)

        # TODO: Store endpoint if provided

        if rate_limit:
            self.rate_limits[name] = rate_limit
            self.rate_limits[name]["last_call"] = 0
            self.rate_limits[name]["count"] = 0
        logger.info(f"API '{name}' registered.")


    async def call_api(self, api_name, method="POST", endpoint_suffix="", data=None, headers=None, params=None, timeout=30):
        """
        Effectue un appel à une API enregistrée.

        Args:
            api_name (str): Nom de l'API à appeler.
            method (str): Méthode HTTP (GET, POST, etc.).
            endpoint_suffix (str): Suffixe à ajouter à l'URL de base de l'API.
            data (dict, optional): Données à envoyer dans le corps de la requête (pour POST/PUT).
            headers (dict, optional): En-têtes HTTP supplémentaires.
            params (dict, optional): Paramètres d'URL (pour GET).
            timeout (int): Délai d'attente pour la requête en secondes.

        Returns:
            dict or None: La réponse JSON de l'API ou None en cas d'erreur.
        """
        if api_name not in self.api_keys:
             # Try to register from config if not explicitly registered
            self.register_api(api_name)
            if api_name not in self.api_keys or not self.api_keys[api_name]:
                 logger.error(f"API '{api_name}' not configured or missing API key.")
                 return None

        # TODO: Get base endpoint for the api_name
        base_url = self.config.get("api_endpoints", {}).get(api_name, "") # Placeholder
        full_url = f"{base_url}{endpoint_suffix}"

        # Prepare headers
        request_headers = {"Authorization": f"Bearer {self.api_keys[api_name]}"} # Common pattern
        if headers:
            request_headers.update(headers)

        # Apply rate limiting
        await self._rate_limit(api_name)

        session = await self._get_session()
        logger.debug(f"Calling {method} {full_url}")
        try:
            async with session.request(
                method,
                full_url,
                json=data,
                headers=request_headers,
                params=params,
                timeout=aiohttp.ClientTimeout(total=timeout)
            ) as response:
                response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
                logger.debug(f"API '{api_name}' call successful (Status: {response.status})")
                # Handle different content types if necessary
                if 'application/json' in response.headers.get('Content-Type', ''):
                    return await response.json()
                else:
                    return await response.read() # Return raw bytes for images/other data
        except aiohttp.ClientResponseError as e:
             logger.error(f"API Error for '{api_name}': {e.status} - {e.message} - URL: {full_url}")
             try:
                 error_details = await e.response.text()
                 logger.error(f"Error details: {error_details[:500]}") # Log first 500 chars
             except Exception:
                 pass # Ignore if reading response fails
             return None
        except asyncio.TimeoutError:
            logger.error(f"API call to '{api_name}' timed out after {timeout} seconds. URL: {full_url}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error calling API '{api_name}': {e}. URL: {full_url}")
            return None

    async def close_session(self):
        """Ferme la session aiohttp."""
        if self.session and not self.session.closed:
            await self.session.close()
            logger.info("API Manager session closed.")

# Example Usage (optional, for testing)
# async def main():
#     config = {"api_keys": {"test_api": "YOUR_API_KEY"}, "api_endpoints": {"test_api": "https://httpbin.org"}}
#     api_manager = APIManager(config)
#     api_manager.register_api("test_api", rate_limit={"limit": 5, "period": 10}) # 5 calls per 10 seconds
#
#     tasks = [api_manager.call_api("test_api", method="GET", endpoint_suffix="/get", params={"arg": i}) for i in range(7)]
#     results = await asyncio.gather(*tasks)
#     print(results)
#     await api_manager.close_session()
#
# if __name__ == "__main__":
#      logging.basicConfig(level=logging.DEBUG)
#      asyncio.run(main()) 